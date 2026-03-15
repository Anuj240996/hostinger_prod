const express = require('express');
const { authenticate } = require('../middleware/auth');
const pool = require('../database/db');
const path = require('path');
const fs = require('fs');

const router = express.Router();

// Create a project (customer) from external data and associate with authenticated user
router.post('/external', authenticate, async (req, res) => {
  try {
    // Determine app owner id (the id under which projects should be listed).
    // Prefer explicit user_app id when available so projects belong to the logged-in app user.
    let appOwnerId = null;
    if (req.user && req.user.auth_source === 'user_app' && req.user.id) {
      appOwnerId = req.user.id;
    } else if (req.user && req.user.id && typeof req.user.id === 'number') {
      appOwnerId = req.user.id;
    } else if (req.user && req.user.auth_user_id) {
      // Fallback to auth_user id if that's all we have
      appOwnerId = req.user.auth_user_id;
    } else if (req.user && req.user.id && typeof req.user.id === 'string') {
      const parsed = parseInt(req.user.id, 10);
      if (!isNaN(parsed)) appOwnerId = parsed;
    }

    if (!appOwnerId) {
      return res.status(401).json({ message: 'Could not identify user' });
    }

    const {
      comp_name,
      consumer,
      first_name,
      last_name,
      email,
      phone,
      address,
      city,
      state,
      location,
    } = req.body;

    // Basic validation
    if (!comp_name && !consumer) {
      return res.status(400).json({ success: false, message: 'comp_name or consumer is required' });
    }

    // Normalize phone and ensure not null (DB constraint)
    const phoneValueRaw = phone ?? req.body.phone ?? '';
    const phoneParam = (typeof phoneValueRaw === 'string' && phoneValueRaw.trim() !== '')
      ? phoneValueRaw.trim()
      : (typeof phoneValueRaw === 'number' ? String(phoneValueRaw) : '0000000000');

    // Ensure required columns (some schemas enforce NOT NULL on plant_capacity)
    const plantCapacityValue = req.body.plant_capacity ?? req.body.plantCapacity ?? 0;

    // If caller provided an external auth_user id, create or update a link between app user and auth_user
    // Store the provided token and return the existing projects for that auth_user WITHOUT creating customer rows.
    const sourceAuthUserId = req.body.source_auth_user_id ?? req.body.sourceAuthUserId ?? null;
    if (sourceAuthUserId) {
      try {
        // Ensure link table exists (with unique constraint on pair)
        await pool.query(`
          CREATE TABLE IF NOT EXISTS app_auth_links (
            id BIGSERIAL PRIMARY KEY,
            app_user_id BIGINT NOT NULL,
            auth_user_id BIGINT NOT NULL,
            token TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (app_user_id, auth_user_id)
          )
        `);

        // Upsert link: insert or update token if exists
        await pool.query(
          `INSERT INTO app_auth_links (app_user_id, auth_user_id, token)
           VALUES ($1, $2, $3)
           ON CONFLICT (app_user_id, auth_user_id) DO UPDATE
             SET token = EXCLUDED.token,
                 created_at = CURRENT_TIMESTAMP`,
          [appOwnerId, sourceAuthUserId, req.body.token ?? null]
        );

        // Fetch existing customer records for that external auth_user (do not create new customers)
        const custRows = await pool.query(
          `SELECT cust_id, consumer, first_name, last_name, email, phone, address, city, state, comp_name
           FROM customer
           WHERE new_customer_id = $1
           ORDER BY cust_id DESC`,
          [sourceAuthUserId]
        );

        const projects = custRows.rows.map(customer => ({
          id: customer.cust_id,
          projectId: customer.cust_id,
          projectName: customer.comp_name || `${customer.first_name || ''} ${customer.last_name || ''}`.trim() || `AF#${customer.consumer || customer.cust_id}`,
          consumer: customer.consumer,
          location: `${customer.city || ''}, ${customer.state || ''}`.trim() || customer.address || 'N/A',
        }));

        return res.json({ success: true, message: 'Linked account and fetched projects', data: { projects } });
      } catch (linkErr) {
        console.error('❌ Error linking app user to auth_user:', linkErr.message);
        // Fall through to standard create flow as a fallback
      }
    }

    // Prevent duplicate customer for the same app user by consumer.
    // If another user has the same consumer, we still allow creating a copy for this app user.
    if (consumer != null) {
      try {
        const existing = await pool.query('SELECT * FROM customer WHERE consumer = $1 AND new_customer_id = $2 LIMIT 1', [consumer, appOwnerId]);
        if (existing.rows.length > 0) {
          const existingRow = existing.rows[0];
          // Return existing record in standardized format
          return res.json({
            success: true,
            message: 'Project already exists',
            data: {
              project: {
                id: existingRow.cust_id,
                projectId: existingRow.cust_id,
                projectName: existingRow.comp_name,
                consumer: existingRow.consumer,
                location: `${existingRow.city || ''}, ${existingRow.state || ''}`.trim() || existingRow.address || 'N/A',
                phone: existingRow.phone,
                email: existingRow.email
              }
            }
          });
        }
      } catch (dupErr) {
        console.error('❌ Error checking existing customer by consumer for this user:', dupErr.message);
        // Continue to attempt insert
      }
      // Check if the consumer exists under any other organization - if so, disallow importing to prevent cross-org assignment
      try {
        const globalExisting = await pool.query('SELECT cust_id, new_customer_id FROM customer WHERE consumer = $1 LIMIT 1', [consumer]);
        if (globalExisting.rows.length > 0) {
          const globalRow = globalExisting.rows[0];
          if (globalRow.new_customer_id && String(globalRow.new_customer_id) !== String(appOwnerId)) {
            return res.status(409).json({
              success: false,
              message: 'Project already assigned to another organization',
              data: {
                projectId: globalRow.cust_id,
                ownerId: globalRow.new_customer_id
              }
            });
          }
        }
      } catch (globalErr) {
        console.error('❌ Error checking global existing customer by consumer:', globalErr.message);
        // proceed with insert as fallback
      }
    }

    // Ensure pincode is always provided (some schemas require NOT NULL)
    const pincodeValueRaw = req.body.pincode ?? req.body.pin ?? '';
    const pincodeParam = (typeof pincodeValueRaw === 'string' && pincodeValueRaw.trim() !== '')
      ? pincodeValueRaw.trim()
      : (typeof pincodeValueRaw === 'number' ? String(pincodeValueRaw) : '000000');

    // Some schemas have a non-null "qunt_solar" column - default to 0 if not provided
    const quntSolarRaw = req.body.qunt_solar ?? req.body.quntSolar ?? 0;
    const quntSolarParam = (typeof quntSolarRaw === 'number') ? quntSolarRaw : (parseInt(quntSolarRaw, 10) || 0);
    // Some schemas also have a non-null "qunt_inv" column - default to 0 if not provided
    const quntInvRaw = req.body.qunt_inv ?? req.body.quntInv ?? 0;
    const quntInvParam = (typeof quntInvRaw === 'number') ? quntInvRaw : (parseInt(quntInvRaw, 10) || 0);
    // Some schemas require an emp_id_id (employee who created/assigned) - default to current app owner
    const empIdRaw = req.body.emp_id ?? req.body.empId ?? appOwnerId;
    const empIdParam = (typeof empIdRaw === 'number') ? empIdRaw : (parseInt(empIdRaw, 10) || appOwnerId);

    // Build an object of fields we intend to insert (start with common ones)
    const fieldsToInsert = {
      comp_name: comp_name || null,
      consumer: consumer || null,
      first_name: first_name || null,
      last_name: last_name || null,
      email: email || null,
      phone: phoneParam,
      address: address || location || null,
      city: city || null,
      state: state || null,
      pincode: pincodeParam,
      qunt_solar: quntSolarParam,
      qunt_inv: quntInvParam,
      plant_capacity: (typeof plantCapacityValue === 'number') ? plantCapacityValue : (parseFloat(plantCapacityValue) || 0),
      emp_id_id: empIdParam,
      new_customer_id: appOwnerId,
    };

    // Query database for NOT NULL columns without defaults and fill sensible fallbacks dynamically
    try {
      const requiredColsRes = await pool.query(`
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'customer' AND is_nullable = 'NO' AND column_default IS NULL
      `);
      requiredColsRes.rows.forEach(col => {
        const name = col.column_name;
        const type = col.data_type || '';
        if (fieldsToInsert[name] === undefined) {
          // Provide a reasonable fallback depending on type
          if (name === 'cust_id' || name === 'id') return; // skip primary key
          if (type.includes('integer') || type.includes('bigint')) {
            fieldsToInsert[name] = 0;
          } else if (type.includes('numeric') || type.includes('decimal')) {
            fieldsToInsert[name] = 0;
          } else if (type.includes('character') || type.includes('text')) {
            fieldsToInsert[name] = '';
          } else if (type.includes('boolean')) {
            fieldsToInsert[name] = false;
          } else if (type.includes('timestamp') || type.includes('date') || type.includes('time')) {
            fieldsToInsert[name] = new Date().toISOString();
          } else {
            // Generic fallback
            fieldsToInsert[name] = null;
          }
        }
      });
    } catch (schemaErr) {
      console.warn('Could not introspect customer table schema; proceeding with provided fields. Error:', schemaErr.message);
    }

    // Build dynamic INSERT using fieldsToInsert
    const insertColumns = Object.keys(fieldsToInsert);
    const insertValues = Object.values(fieldsToInsert);
    const placeholders = insertValues.map((_, i) => `$${i + 1}`).join(',');
    const insertQuery = `INSERT INTO customer (${insertColumns.join(',')}) VALUES (${placeholders}) RETURNING *`;

    console.log('🔵 Creating external project with params:', insertValues);
    let insertResult;
    try {
      insertResult = await pool.query(insertQuery, insertValues);
    } catch (insertErr) {
      console.error('❌ Error creating external project - SQL error:', insertErr.message);
      console.error('   Query:', insertQuery.replace(/\s+/g, ' ').trim());
      console.error('   Params:', insertValues);
      return res.status(500).json({ message: 'Server error creating project', error: insertErr.message });
    }
    const row = insertResult.rows[0];

    // Build project object in the same shape as GET /projects returns
    const project = {
      id: row.cust_id,
      projectId: row.cust_id,
      projectName: row.comp_name || row.consumer || `AF#${row.cust_id}`,
      consumer: row.consumer,
      location: `${row.city || ''}, ${row.state || ''}`.trim().replace(/^,\s*/, '').replace(/,\s*$/, '') || (row.address || 'N/A'),
      status: 'Pending',
      plantCapacity: String(row.plant_capacity || '0'),
      powerGeneration: '0',
      projectImage: null,
      customerId: row.cust_id,
      phone: row.phone,
      email: row.email,
    };

    // Return created project
    res.status(201).json({ success: true, message: 'Project created', data: { project } });
  } catch (err) {
    console.error('Error creating external project:', err.message);
    res.status(500).json({ message: 'Server error creating project', error: err.message });
  }
});

// Helper function to convert bit varying to boolean
function bitToBoolean(bitValue) {
  if (bitValue === null || bitValue === undefined) return false;
  if (typeof bitValue === 'boolean') return bitValue;
  if (typeof bitValue === 'string') {
    // PostgreSQL bit varying returns as string like '1' or '0'
    return bitValue === '1' || bitValue.toLowerCase() === 'true';
  }
  if (typeof bitValue === 'number') return bitValue === 1;
  return false;
}

// Helper function to get auth_user_id from req.user
function getAuthUserId(req) {
  if (req.user && req.user.auth_user_id) {
    return req.user.auth_user_id;
  }
  // Only consider req.user.id as auth_user id if the auth source is explicitly auth_user
  if (req.user && req.user.auth_source === 'auth_user') {
    if (req.user.id && typeof req.user.id === 'number') {
      return req.user.id;
    } else if (req.user.id && typeof req.user.id === 'string') {
      const userIdNum = parseInt(req.user.id, 10);
      if (!isNaN(userIdNum) && req.user.id === userIdNum.toString()) {
        return userIdNum;
      }
    }
  }
  return null;
}

// Get all projects for authenticated customer
router.get('/', authenticate, async (req, res) => {
  try {
    // Disable caching for project lists to avoid 304 Not Modified responses
    res.set('Cache-Control', 'no-store, no-cache, must-revalidate, private');
    // Determine app owner id (the id under which projects should be listed).
    let appOwnerId = null;
    if (req.user && req.user.auth_source === 'user_app' && req.user.id) {
      appOwnerId = req.user.id;
    } else if (req.user && req.user.id && typeof req.user.id === 'number') {
      appOwnerId = req.user.id;
    } else if (req.user && req.user.auth_user_id) {
      appOwnerId = req.user.auth_user_id;
    } else if (req.user && req.user.id && typeof req.user.id === 'string') {
      const parsed = parseInt(req.user.id, 10);
      if (!isNaN(parsed)) appOwnerId = parsed;
    }

    if (!appOwnerId) {
      return res.status(401).json({
        message: 'Could not identify user',
        projects: []
      });
    }

    // Get linked external auth_user ids (if any) so we can show their projects too
    let linkedAuthIds = [];
    try {
      const linkRows = await pool.query(
        `SELECT auth_user_id FROM app_auth_links WHERE app_user_id = $1`,
        [appOwnerId]
      );
      linkedAuthIds = linkRows.rows.map(r => r.auth_user_id).filter(Boolean);
    } catch (linkErr) {
      // If table doesn't exist yet, continue without links
      linkedAuthIds = [];
    }

    // Get all customer records for this app owner OR for any linked auth_user ids
    // A user can have multiple customer records (projects)
    let customerResult;
    if (linkedAuthIds.length > 0) {
      customerResult = await pool.query(
        `SELECT cust_id, consumer, first_name, last_name, middle_name, 
                email, phone, address, city, state, comp_name, new_customer_id
         FROM customer
         WHERE new_customer_id = $1 OR new_customer_id = ANY($2)
         ORDER BY cust_id DESC`,
        [appOwnerId, linkedAuthIds]
      );
    } else {
      customerResult = await pool.query(
        `SELECT cust_id, consumer, first_name, last_name, middle_name, 
                email, phone, address, city, state, comp_name, new_customer_id
         FROM customer
         WHERE new_customer_id = $1
         ORDER BY cust_id DESC`,
        [appOwnerId]
      );
    }

    if (customerResult.rows.length === 0) {
      return res.json({ 
        projects: [],
        message: 'No projects found for this user'
      });
    }

    // Get project details for each customer
    const projects = await Promise.all(
      customerResult.rows.map(async (customer) => {
        const custId = customer.cust_id;
        
        // Get customer_result to calculate status
        // Relationship: customer_result.consumer_id_id = customer.cust_id
        let customerResultData = null;
        try {
          let resultQuery;
          // First try: match by consumer_id_id (the correct column name)
          try {
            resultQuery = await pool.query(
              `SELECT solar_panel, inverter, net_meter, mseb, inspection_report
               FROM customer_result
               WHERE consumer_id_id = $1
               ORDER BY id DESC
               LIMIT 1`,
              [custId]
            );
            if (resultQuery.rows.length > 0) {
              customerResultData = resultQuery.rows[0];
            }
          } catch (e1) {
            // If consumer_id_id doesn't exist or fails, try matching by consumer text field
            if (customer.consumer) {
              try {
                resultQuery = await pool.query(
                  `SELECT solar_panel, inverter, net_meter, mseb, inspection_report
                   FROM customer_result
                   WHERE consumer = $1
                   ORDER BY id DESC
                   LIMIT 1`,
                  [customer.consumer]
                );
                if (resultQuery.rows.length > 0) {
                  customerResultData = resultQuery.rows[0];
                }
              } catch (e2) {
                console.log('Error fetching customer_result by consumer:', e2.message);
              }
            }
          }
        } catch (e) {
          console.log('Error fetching customer_result for cust_id', custId, ':', e.message);
        }

        // Calculate project status based on customer_result
        let status = 'Pending';
        if (customerResultData) {
          const solarPanel = bitToBoolean(customerResultData.solar_panel);
          const inverter = bitToBoolean(customerResultData.inverter);
          const netMeter = bitToBoolean(customerResultData.net_meter);
          const mseb = bitToBoolean(customerResultData.mseb);
          const inspectionReport = bitToBoolean(customerResultData.inspection_report);

          // If inspection_report is true, treat project as Completed (per requirement)
          if (inspectionReport) {
            status = 'Completed';
          } else {
            // Status is "Completed" only if ALL components are completed
            if (solarPanel && inverter && netMeter && mseb && inspectionReport) {
              status = 'Completed';
            } else {
              status = 'Pending';
            }
          }
        } else {
          console.log('⚠️ No customer_result found for cust_id:', custId, 'consumer:', customer.consumer);
        }

        // Get plant capacity from customer_result or default
        let plantCapacity = '0';
        let powerGeneration = '0';
        try {
          // Try to get from customer_result or calculate from barcode images
          const assetOwnerId = customer.new_customer_id || appOwnerId;
          const capacityQuery = await pool.query(
            `SELECT wattage
             FROM detect_barcodes_barcodeimage
             WHERE assignto_id = $1
             ORDER BY id DESC
             LIMIT 1`,
            [assetOwnerId]
          );
          if (capacityQuery.rows.length > 0 && capacityQuery.rows[0].wattage) {
            plantCapacity = capacityQuery.rows[0].wattage.toString();
            powerGeneration = plantCapacity; // Default to same for now
          }
        } catch (e) {
          console.log('Error fetching capacity:', e.message);
        }

        // Generate project name from customer info
        const projectName = customer.comp_name || 
                           `${customer.first_name || ''} ${customer.middle_name || ''} ${customer.last_name || ''}`.trim() ||
                           `AF#${customer.consumer || customer.cust_id}`;

        return {
          id: customer.cust_id,
          projectId: customer.cust_id,
          projectName: projectName,
          consumer: customer.consumer,
          location: `${customer.city || ''}, ${customer.state || ''}`.trim().replace(/^,\s*/, '').replace(/,\s*$/, '') || 'N/A',
          status: status,
          plantCapacity: plantCapacity,
          powerGeneration: powerGeneration,
          projectImage: null, // Will be added later if available
          customerId: customer.cust_id,
        };
      })
    );

    res.json({ projects });
  } catch (error) {
    console.error('Get projects error:', error);
    res.status(500).json({ 
      message: 'Server error', 
      projects: [],
      error: process.env.NODE_ENV === 'development' ? error.message : undefined 
    });
  }
});

// Get project details with products
router.get('/:projectId', authenticate, async (req, res) => {
  try {
    // Disable caching for project details to avoid 304 Not Modified responses
    res.set('Cache-Control', 'no-store, no-cache, must-revalidate, private');
    const authUserId = getAuthUserId(req);
    const projectId = parseInt(req.params.projectId, 10);

    if (!authUserId) {
      return res.status(401).json({ message: 'Could not identify user' });
    }

    if (isNaN(projectId)) {
      return res.status(400).json({ message: 'Invalid project ID' });
    }

    // Get customer record by cust_id (do not strictly enforce new_customer_id ownership here)
    const customerResult = await pool.query(
      `SELECT cust_id, consumer, first_name, last_name, middle_name, 
              email, phone, address, city, state, comp_name, new_customer_id,
              qunt_solar, qunt_inv, sol_warranty, inv_warranty, com_warranty
       FROM customer
       WHERE cust_id = $1
       LIMIT 1`,
      [projectId]
    );

    if (customerResult.rows.length === 0) {
      return res.status(404).json({ message: 'Project not found' });
    }

    const customer = customerResult.rows[0];

    // Determine which assignto_id should be used to lookup barcode images and related assets.
    // Prefer the customer.new_customer_id (which is typically the auth_user id from source system).
    // If not present, fall back to the authenticated app user's id so existing flow continues.
    const assetOwnerId = customer.new_customer_id || authUserId;
    if (customer.new_customer_id && String(customer.new_customer_id) !== String(authUserId)) {
      console.log(`ℹ️ Project ${projectId} belongs to auth_user ${customer.new_customer_id}; using that id to fetch barcode images.`);
    }

    // Get customer_result
    // Relationship: customer_result.consumer_id_id = customer.cust_id
    let customerResultData = null;
    try {
      let resultQuery;
      // First try: match by consumer_id_id (the correct column name)
      try {
        resultQuery = await pool.query(
          `SELECT solar_panel, inverter, net_meter, mseb, inspection_report
           FROM customer_result
           WHERE consumer_id_id = $1
           ORDER BY id DESC
           LIMIT 1`,
          [projectId]
        );
        if (resultQuery.rows.length > 0) {
          customerResultData = resultQuery.rows[0];
        }
      } catch (e1) {
        // If consumer_id_id doesn't exist or fails, try matching by consumer text field
        if (customer.consumer) {
          try {
            resultQuery = await pool.query(
              `SELECT solar_panel, inverter, net_meter, mseb, inspection_report
               FROM customer_result
               WHERE consumer = $1
               ORDER BY id DESC
               LIMIT 1`,
              [customer.consumer]
            );
            if (resultQuery.rows.length > 0) {
              customerResultData = resultQuery.rows[0];
            }
          } catch (e2) {
            console.log('Error fetching customer_result by consumer:', e2.message);
          }
        }
      }
    } catch (e) {
      console.log('Error fetching customer_result:', e.message);
    }

    // Calculate status (inspection_report true => Completed)
    let status = 'Pending';
    if (customerResultData) {
      const inspectionReport = bitToBoolean(customerResultData.inspection_report);
      const allCompleted = [
        customerResultData.solar_panel,
        customerResultData.inverter,
        customerResultData.net_meter,
        customerResultData.mseb,
        customerResultData.inspection_report
      ].every(val => val === 1 || val === '1' || val === true);
      if (inspectionReport) {
        status = 'Active';
      } else {
        status = allCompleted ? 'Active' : 'Pending';
      }
    }

    // Get electricity production, storage, and total panels from barcode images
    let electricityProduction = '0';
    let storageOrInGrid = '0';
    let totalPanel = '0';

    try {
      const barcodeQuery = await pool.query(
        `SELECT 
          SUM(CASE WHEN product_name ILIKE '%SolarPanel%' OR product_name ILIKE '%Solar Panel%' THEN CAST(wattage AS NUMERIC) ELSE 0 END) as total_solar_wattage,
          COUNT(CASE WHEN product_name ILIKE '%SolarPanel%' OR product_name ILIKE '%Solar Panel%' THEN 1 END) as solar_count,
          SUM(CASE WHEN product_name ILIKE '%Battery%' OR product_name ILIKE '%Storage%' THEN CAST(wattage AS NUMERIC) ELSE 0 END) as storage_wattage
         FROM detect_barcodes_barcodeimage
        WHERE assignto_id = $1`,
        [assetOwnerId]
      );

      if (barcodeQuery.rows.length > 0) {
        const row = barcodeQuery.rows[0];
        electricityProduction = row.total_solar_wattage ? Math.round(row.total_solar_wattage / 1000).toString() : '0';
        storageOrInGrid = row.storage_wattage ? Math.round(row.storage_wattage / 1000).toString() : '0';
        totalPanel = row.solar_count ? row.solar_count.toString() : '0';
      }
    } catch (e) {
      console.log('Error fetching barcode data:', e.message);
    }

    // Fetch warranty and quantity fields from customer table (already selected earlier)
    let solWarranty = null;
    let invWarranty = null;
    let omWarranty = null;
    let quntSolar = null;
    let quntInv = null;
    try {
      solWarranty = customer.sol_warranty || null;
      invWarranty = customer.inv_warranty || null;
      omWarranty = customer.com_warranty || null;
      quntSolar = customer.qunt_solar || 0;
      quntInv = customer.qunt_inv || 0;
    } catch (e) {
      // ignore missing columns
    }

    // Get installation date from customer_mseb to compute warranty start/end
    let installationDateFromMseb = null;
    try {
      const msebDateQuery = await pool.query(
        `SELECT installation_date_date
         FROM customer_mseb
         WHERE customer_id = $1
         ORDER BY id DESC
         LIMIT 1`,
        [customer.cust_id]
      );
      if (msebDateQuery.rows.length > 0 && msebDateQuery.rows[0].installation_date_date) {
        installationDateFromMseb = msebDateQuery.rows[0].installation_date_date;
      }
    } catch (e) {
      // ignore
    }

    // Compute warranty start/end strings if installation date available and warranty years present
    let solWarrantyStart = null, solWarrantyEnd = null;
    let invWarrantyStart = null, invWarrantyEnd = null;
    let omWarrantyStart = null, omWarrantyEnd = null;
    try {
      if (installationDateFromMseb) {
        const installationDate = new Date(installationDateFromMseb);
        if (solWarranty) {
          solWarrantyStart = installationDate.toISOString().split('T')[0];
          const end = new Date(installationDate);
          end.setFullYear(end.getFullYear() + parseInt(solWarranty));
          solWarrantyEnd = end.toISOString().split('T')[0];
        }
        if (invWarranty) {
          invWarrantyStart = installationDate.toISOString().split('T')[0];
          const end = new Date(installationDate);
          end.setFullYear(end.getFullYear() + parseInt(invWarranty));
          invWarrantyEnd = end.toISOString().split('T')[0];
        }
        if (omWarranty) {
          omWarrantyStart = installationDate.toISOString().split('T')[0];
          const end = new Date(installationDate);
          end.setFullYear(end.getFullYear() + parseInt(omWarranty));
          omWarrantyEnd = end.toISOString().split('T')[0];
        }
      }
    } catch (e) {
      // ignore
    }

    // Get net meter counts
    let netMeterTotal = 0;
    let netMeterUsed = 0;
    try {
      const netCount = await pool.query(
        `SELECT COUNT(*)::int as total FROM customer_meters WHERE customer_id = $1`,
        [customer.cust_id]
      );
      netMeterTotal = netCount.rows[0]?.total ?? 0;
      const netUsed = await pool.query(
        `SELECT COUNT(*)::int as used FROM customer_meters WHERE customer_id = $1 AND serial_no IS NOT NULL`,
        [customer.cust_id]
      );
      netMeterUsed = netUsed.rows[0]?.used ?? 0;
    } catch (e) {
      // ignore
    }
    // Get products (solar panels and inverters from barcode images)
    const products = [];
    try {
      // Determine app owner id (useful to look up linked auth_user ids)
      let appOwnerId = null;
      if (req.user && req.user.auth_source === 'user_app' && req.user.id) {
        appOwnerId = req.user.id;
      } else if (req.user && req.user.id && typeof req.user.id === 'number') {
        appOwnerId = req.user.id;
      } else if (req.user && req.user.auth_user_id) {
        appOwnerId = req.user.auth_user_id;
      } else if (req.user && req.user.id && typeof req.user.id === 'string') {
        const parsed = parseInt(req.user.id, 10);
        if (!isNaN(parsed)) appOwnerId = parsed;
      }

      // First try: fetch products using the project's asset owner id (usually customer.new_customer_id)
      let productsRows = [];
      const baseQuery = `
        SELECT id, barcode_data, product_name, company, wattage, barcode_type, file_saved_at, company_name
        FROM detect_barcodes_barcodeimage
        WHERE (product_name ILIKE '%SolarPanel%' OR product_name ILIKE '%Solar Panel%' OR product_name ILIKE '%Inverter%')
          AND assignto_id = $1
        ORDER BY id DESC
      `;
      const rows1 = await pool.query(baseQuery, [assetOwnerId]);
      productsRows = rows1.rows || [];

      // If none found, try linked ids: appOwnerId, any auth_user ids linked to this app user, and customer.new_customer_id
      if ((!productsRows || productsRows.length === 0)) {
        let linkedIds = [];
        try {
          const linkRes = await pool.query('SELECT auth_user_id FROM app_auth_links WHERE app_user_id = $1', [appOwnerId]);
          linkedIds = linkRes.rows.map(r => r.auth_user_id).filter(Boolean);
        } catch (linkErr) {
          // ignore if table missing
          linkedIds = [];
        }

        const candidateIds = [assetOwnerId, appOwnerId, ...linkedIds].filter(Boolean);
        // Remove duplicates
        const uniqueIds = [...new Set(candidateIds)];
        if (uniqueIds.length > 0) {
          const q = await pool.query(
            `SELECT id, barcode_data, product_name, company, wattage, barcode_type, file_saved_at, company_name
             FROM detect_barcodes_barcodeimage
             WHERE (product_name ILIKE '%SolarPanel%' OR product_name ILIKE '%Solar Panel%' OR product_name ILIKE '%Inverter%')
               AND assignto_id = ANY($1)
             ORDER BY id DESC`,
            [uniqueIds]
          );
          productsRows = q.rows || [];
        }
      }

      productsRows.forEach((row) => {
        products.push({
          id: row.id,
          productId: row.barcode_data || `PROD-${row.id}`,
          productImage: row.barcode_path || null,
          brand: row.company || row.company_name || 'Unknown Brand',
          model: row.product_name || 'Unknown Model',
          wattage: row.wattage ? `${row.wattage} Wp` : null,
          quantity: 1,
          warranty: '25 year', // Default warranty
          warrantyStart: null,
          warrantyEnd: null,
          price: null,
          tax: null,
          taxPercent: 18,
          assigntoId: row.assignto_id || null,
        });
      });
    } catch (e) {
      console.log('Error fetching products:', e.message);
    }

    const projectName = customer.comp_name || 
                       `${customer.first_name || ''} ${customer.middle_name || ''} ${customer.last_name || ''}`.trim() ||
                       `AF#${customer.consumer || customer.cust_id}`;

    // Get installation progress data similar to progress.js route
    let progressData = null;
    try {
      // Get customer_result for progress calculation
      // Relationship: customer_result.consumer_id_id = customer.cust_id
      let resultQuery;
      let hasResult = false;
      
      // First try: match by consumer_id_id (the correct column name)
      try {
        resultQuery = await pool.query(
          `SELECT solar_panel, inverter, net_meter, mseb, inspection_report
           FROM customer_result
           WHERE consumer_id_id = $1
           ORDER BY id DESC
           LIMIT 1`,
          [projectId]
        );
        if (resultQuery.rows.length > 0) {
          hasResult = true;
        }
      } catch (e1) {
        // If consumer_id_id doesn't exist or fails, try matching by consumer text field
        if (customer.consumer) {
          try {
            resultQuery = await pool.query(
              `SELECT solar_panel, inverter, net_meter, mseb, inspection_report
               FROM customer_result
               WHERE consumer = $1
               ORDER BY id DESC
               LIMIT 1`,
              [customer.consumer]
            );
            if (resultQuery.rows.length > 0) {
              hasResult = true;
            }
          } catch (e2) {
            console.log('Error fetching customer_result by consumer for progress:', e2.message);
          }
        }
      }
      
      if (hasResult && resultQuery.rows.length > 0) {
        const resultRow = resultQuery.rows[0];
        const solarPanel = bitToBoolean(resultRow.solar_panel);
        const inverter = bitToBoolean(resultRow.inverter);
        const netMeter = bitToBoolean(resultRow.net_meter);
        const mseb = bitToBoolean(resultRow.mseb);
        const inspectionReport = bitToBoolean(resultRow.inspection_report);

        // Calculate percentages
        const completedCount = [solarPanel, inverter, netMeter, mseb, inspectionReport].filter(Boolean).length;
        const percentage = (completedCount / 5) * 100;
        const allCompleted = completedCount === 5;

        // Get customer warranty years and MSEB installation date
        let solWarrantyYears = null;
        let invWarrantyYears = null;
        let installationDateFromMseb = null;
        
        try {
          const customerWarrantyQuery = await pool.query(
            `SELECT sol_warranty, inv_warranty
             FROM customer
             WHERE cust_id = $1
             LIMIT 1`,
            [projectId]
          );
          if (customerWarrantyQuery.rows.length > 0) {
            solWarrantyYears = customerWarrantyQuery.rows[0].sol_warranty;
            invWarrantyYears = customerWarrantyQuery.rows[0].inv_warranty;
          }
        } catch (e) {
          console.log('Error fetching warranty years:', e.message);
        }

        // Get installation_date_date from customer_mseb table
        try {
          const msebDateQuery = await pool.query(
            `SELECT installation_date_date
             FROM customer_mseb
             WHERE customer_id = $1
             ORDER BY id DESC
             LIMIT 1`,
            [projectId]
          );
          if (msebDateQuery.rows.length > 0 && msebDateQuery.rows[0].installation_date_date) {
            installationDateFromMseb = msebDateQuery.rows[0].installation_date_date;
          }
        } catch (e) {
          console.log('Error fetching MSEB installation date:', e.message);
        }

        // Calculate warranty dates using MSEB installation_date_date
        let solarPanelWarrantyStart = null;
        let solarPanelWarrantyEnd = null;
        let inverterWarrantyStart = null;
        let inverterWarrantyEnd = null;
        
        if (installationDateFromMseb) {
          const installationDate = new Date(installationDateFromMseb);
          if (solWarrantyYears) {
            solarPanelWarrantyStart = installationDate.toISOString().split('T')[0];
            const endDate = new Date(installationDate);
            endDate.setFullYear(endDate.getFullYear() + parseInt(solWarrantyYears) || 25);
            solarPanelWarrantyEnd = endDate.toISOString().split('T')[0];
          }
          if (invWarrantyYears) {
            inverterWarrantyStart = installationDate.toISOString().split('T')[0];
            const endDate = new Date(installationDate);
            endDate.setFullYear(endDate.getFullYear() + parseInt(invWarrantyYears) || 25);
            inverterWarrantyEnd = endDate.toISOString().split('T')[0];
          }
        }

        // Get Solar Panel serial, company name, solar type, quantity, and wattage
        let solarPanelSerial = null;
        let solarPanelCompany = null;
        let solarPanelType = null;
        let solarPanelQuantity = 0;
        let solarPanelWattage = null;
        if (solarPanel) {
          try {
            // Get all solar panels to count quantity and get wattage
            const solarQuery = await pool.query(
              `SELECT barcode_data, company_name, company, stock_id, wattage
               FROM detect_barcodes_barcodeimage
               WHERE (product_name ILIKE '%SolarPanel%' OR product_name ILIKE '%Solar Panel%')
                 AND assignto_id = $1
               ORDER BY id DESC`,
             [assetOwnerId]
            );
            if (solarQuery.rows.length > 0) {
              solarPanelQuantity = solarQuery.rows.length;
              const row = solarQuery.rows[0]; // Get first row for serial, company, etc.
              solarPanelSerial = row.barcode_data || null;
              solarPanelCompany = row.company_name || row.company || null;
              solarPanelWattage = row.wattage ? `${row.wattage} Wp` : null;
              
              // Get solar type separately if stock_id exists
              if (row.stock_id) {
                try {
                  const solarTypeQuery = await pool.query(
                    `SELECT inv_stock.name as solar_type
                     FROM transactions_purchaseserial tps
                     LEFT JOIN inventory_stock inv_stock ON inv_stock.id = tps.stock_id
                     WHERE tps.stock_id = $1
                     LIMIT 1`,
                    [row.stock_id]
                  );
                  if (solarTypeQuery.rows.length > 0 && solarTypeQuery.rows[0].solar_type) {
                    solarPanelType = solarTypeQuery.rows[0].solar_type;
                  }
                } catch (typeError) {
                  console.log('Error fetching solar type:', typeError.message);
                }
              }
            }
          } catch (e) {
            console.log('Error fetching solar panel details:', e.message);
            console.error(e);
          }
        }

        // Get Inverter serial, company name, quantity, and wattage
        let inverterSerial = null;
        let inverterCompany = null;
        let inverterQuantity = 0;
        let inverterWattage = null;
        if (inverter) {
          try {
            // Get all inverters to count quantity and get wattage
            const inverterQuery = await pool.query(
              `SELECT barcode_data, company_name, company, wattage
               FROM detect_barcodes_barcodeimage
               WHERE product_name ILIKE '%Inverter%'
                 AND assignto_id = $1
               ORDER BY id DESC`,
             [assetOwnerId]
            );
            if (inverterQuery.rows.length > 0) {
              inverterQuantity = inverterQuery.rows.length;
              const row = inverterQuery.rows[0]; // Get first row for serial, company, etc.
              if (row.barcode_data) {
                inverterSerial = row.barcode_data;
              }
              inverterCompany = row.company_name || row.company || null;
              inverterWattage = row.wattage ? `${row.wattage} Wp` : null;
            }
          } catch (e) {
            console.log('Error fetching inverter details:', e.message);
          }
        }

        // Get Net Meter details
        let netMeterDetails = null;
        if (netMeter) {
          try {
            const netMeterQuery = await pool.query(
              `SELECT serial_no, make, capacity, meter_type
               FROM customer_meters
               WHERE customer_id = $1
               ORDER BY id DESC
               LIMIT 1`,
              [projectId]
            );
            if (netMeterQuery.rows.length > 0) {
              netMeterDetails = {
                serialNo: netMeterQuery.rows[0].serial_no || null,
                make: netMeterQuery.rows[0].make || null,
                capacity: netMeterQuery.rows[0].capacity || null,
                meterType: netMeterQuery.rows[0].meter_type || null,
              };
            }
          } catch (e) {
            console.log('Error fetching net meter details:', e.message);
          }
        }

        // Get MSEB details with step dates
        let msebDetails = null;
        if (mseb) {
          try {
            const msebQuery = await pool.query(
              `SELECT load_extension, flisibility, quotation, sent_to_bill, net_meter, 
                      flexibility, approval, meter_testing, agreement, release, installation_date,
                      load_extension_date, flisibility_date, quotation_date, sent_to_bill_date, 
                      net_meter_date, flexibility_date, approval_date, meter_testing_date, 
                      agreement_date, release_date, installation_date_date
               FROM customer_mseb
               WHERE customer_id = $1
               ORDER BY id DESC
               LIMIT 1`,
              [projectId]
            );
            if (msebQuery.rows.length > 0) {
              const msebData = msebQuery.rows[0];
              
              // Check if we should skip initial steps (load_extension, flisibility, quotation, sent_to_bill)
              // Condition: 
              // - load_extension = 0, flisibility = 0, quotation = 0, sent_to_bill = 0 (not completed)
              // - AND net_meter = 1 (completed) AND net_meter_date is not null
              // Then: Hide initial 4 steps, start from Net meter
              
              const netMeterCompleted = bitToBoolean(msebData.net_meter);
              const netMeterDate = msebData.net_meter_date;
              
              // Check if initial steps have value 0 (not completed)
              // A value is considered 0/not completed if it's 0, '0', false, null, undefined, or empty string
              const isNotCompleted = (value) => {
                return value == null || value === '' || value === 0 || value === '0' || value === false || value === undefined;
              };
              
              const loadExtensionNotCompleted = isNotCompleted(msebData.load_extension);
              const flisibilityNotCompleted = isNotCompleted(msebData.flisibility); // Note: flisibility (misspelled field)
              const quotationNotCompleted = isNotCompleted(msebData.quotation);
              const sentToBillNotCompleted = isNotCompleted(msebData.sent_to_bill);
              
              // Should skip initial steps if:
              // - All 4 initial steps have value 0 (not completed)
              // - AND net_meter has value 1 (completed) AND net_meter_date is not null
              const shouldSkipInitialSteps = loadExtensionNotCompleted &&
                                            flisibilityNotCompleted &&
                                            quotationNotCompleted &&
                                            sentToBillNotCompleted &&
                                            netMeterCompleted && 
                                            netMeterDate != null && 
                                            netMeterDate !== '';
              
              // Build steps with dates in correct sequence
              // Sequence: Load extension, Flisibility, Quotation, Sent to bill, Net meter, Technical Flexibility, Approval, Meter Testing, Net meter Agreement, Meter Release, Meter Installation Date
              const msebStepsMap = {};
              
              // Only include initial 4 steps if they should NOT be skipped
              if (!shouldSkipInitialSteps) {
                // 1. Load Extension
                msebStepsMap.loadExtension = {
                  completed: bitToBoolean(msebData.load_extension),
                  date: msebData.load_extension_date || null,
                };
                
                // 2. Flisibility (note: this is the misspelled field "flisibility")
                msebStepsMap.flisibility = {
                  completed: bitToBoolean(msebData.flisibility),
                  date: msebData.flisibility_date || null,
                };
                
                // 3. Quotation
                msebStepsMap.quotation = {
                  completed: bitToBoolean(msebData.quotation),
                  date: msebData.quotation_date || null,
                };
                
                // 4. Sent to Bill
                msebStepsMap.sentToBill = {
                  completed: bitToBoolean(msebData.sent_to_bill),
                  date: msebData.sent_to_bill_date || null,
                };
              }
              // If shouldSkipInitialSteps is true, we skip these 4 steps and start from Net Meter
              
              // Always include these steps (after initial 4 or starting here if skipped)
              // 5. Net Meter
              msebStepsMap.netMeter = {
                completed: bitToBoolean(msebData.net_meter),
                date: msebData.net_meter_date || null,
              };
              
              // 6. Technical Flexibility (note: this is the "flexibility" field - different from "flisibility")
              msebStepsMap.technicalFlexibility = {
                completed: bitToBoolean(msebData.flexibility),
                date: msebData.flexibility_date || null,
              };
              
              // 7. Approval
              msebStepsMap.approval = {
                completed: bitToBoolean(msebData.approval),
                date: msebData.approval_date || null,
              };
              
              // 8. Meter Testing
              msebStepsMap.meterTesting = {
                completed: bitToBoolean(msebData.meter_testing),
                date: msebData.meter_testing_date || null,
              };
              
              // 9. Net meter Agreement
              msebStepsMap.agreement = {
                completed: bitToBoolean(msebData.agreement),
                date: msebData.agreement_date || null,
              };
              
              // 10. Meter Release
              msebStepsMap.release = {
                completed: bitToBoolean(msebData.release),
                date: msebData.release_date || null,
              };
              
              // 11. Meter Installation Date
              msebStepsMap.installationDate = {
                completed: bitToBoolean(msebData.installation_date),
                date: msebData.installation_date_date || null,
              };
              
              // Calculate progress based on visible steps only
              // If initial 4 steps are hidden, they won't be in msebStepsMap, so progress calculation automatically excludes them
              const msebSteps = Object.values(msebStepsMap);
              const completedMsebSteps = msebSteps.filter(step => step.completed).length;
              const totalMsebSteps = msebSteps.length;
              const msebPercentage = totalMsebSteps > 0 ? (completedMsebSteps / totalMsebSteps) * 100 : 0;

              msebDetails = {
                progress: msebPercentage.toFixed(1),
                completedSteps: completedMsebSteps,
                totalSteps: totalMsebSteps, // Only includes visible steps
                steps: msebStepsMap, // Includes only filtered/visible steps with dates
              };
            }
          } catch (e) {
            console.log('Error fetching MSEB details:', e.message);
          }
        }

        progressData = {
          projectStatus: allCompleted ? 'Completed' : 'Pending',
          percentage: percentage.toFixed(1),
          solarPanel: {
            status: solarPanel ? 'Completed' : 'Pending',
            completed: solarPanel,
            serialNo: solarPanelSerial,
            companyName: solarPanelCompany,
            solarType: solarPanelType,
            quantity: solarPanelQuantity,
            wattage: solarPanelWattage,
            warrantyYears: solWarrantyYears,
            warrantyStart: solarPanelWarrantyStart,
            warrantyEnd: solarPanelWarrantyEnd,
          },
          inverter: {
            status: inverter ? 'Completed' : 'Pending',
            completed: inverter,
            serialNo: inverterSerial,
            companyName: inverterCompany,
            quantity: inverterQuantity,
            wattage: inverterWattage,
            warrantyYears: invWarrantyYears,
            warrantyStart: inverterWarrantyStart,
            warrantyEnd: inverterWarrantyEnd,
          },
          netMeter: {
            status: netMeter ? 'Completed' : 'Pending',
            completed: netMeter,
            serialNo: netMeterDetails?.serialNo,
            details: netMeterDetails,
          },
          mseb: {
            status: mseb ? 'Completed' : 'Pending',
            completed: mseb,
            details: msebDetails,
          },
          inspectionReport: {
            status: inspectionReport ? 'Completed' : 'Pending',
            completed: inspectionReport,
          },
        };
      }
    } catch (e) {
      console.log('❌ Error fetching progress data:', e.message);
      console.log('Error stack:', e.stack);
    }

    const project = {
      id: customer.cust_id,
      projectId: customer.cust_id,
      projectName: projectName,
      consumer: customer.consumer,
      location: `${customer.city || ''}, ${customer.state || ''}`.trim().replace(/^,\s*/, '').replace(/,\s*$/, '') || 'N/A',
      status: status,
      plantCapacity: electricityProduction || '0',
      powerGeneration: electricityProduction || '0',
      electricityProduction: electricityProduction,
      storageOrInGrid: storageOrInGrid,
      totalPanel: totalPanel,
      projectImage: null,
      products: products,
      progress: progressData, // Include progress data
      // Quantities from customer record (preferred over barcode counts)
      quantities: {
        solar: quntSolar ?? 0,
        inverter: quntInv ?? 0,
        netMeter: {
          total: netMeterTotal,
          used: netMeterUsed
        }
      },
      // Warranty info (computed from customer warranty years and MSEB installation date)
      warranties: {
        solar: {
          years: solWarranty ?? null,
          start: solWarrantyStart,
          end: solWarrantyEnd
        },
        inverter: {
          years: invWarranty ?? null,
          start: invWarrantyStart,
          end: invWarrantyEnd
        },
        om: {
          years: omWarranty ?? null,
          start: omWarrantyStart,
          end: omWarrantyEnd
        }
      },
    };

    console.log('✅ Project details response - Progress data included:', progressData ? 'Yes' : 'No');
    res.json({ project });
  } catch (error) {
    console.error('Get project details error:', error);
    res.status(500).json({ 
      message: 'Server error',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined 
    });
  }
});

// Get product details
router.get('/products/:productId', authenticate, async (req, res) => {
  try {
    const authUserId = getAuthUserId(req);
    const productId = req.params.productId;

    if (!authUserId) {
      return res.status(401).json({ message: 'Could not identify user' });
    }

    // Get product from barcode image table
    const productQuery = await pool.query(
      `SELECT id, barcode_data, product_name, company, wattage, 
              barcode_type, file_saved_at, company_name, barcode_path
       FROM detect_barcodes_barcodeimage
       WHERE (barcode_data = $1 OR id::text = $1)
         AND assignto_id = $2
       LIMIT 1`,
      [productId, authUserId]
    );

    if (productQuery.rows.length === 0) {
      // Fallback: try to find product globally (without assignto_id filter)
      try {
        const globalQuery = await pool.query(
          `SELECT id, barcode_data, product_name, company, wattage, 
                  barcode_type, file_saved_at, company_name, barcode_path, assignto_id
           FROM detect_barcodes_barcodeimage
           WHERE barcode_data = $1 OR id::text = $1
           LIMIT 1`,
          [productId]
        );
        if (globalQuery.rows.length === 0) {
          return res.status(404).json({ message: 'Product not found' });
        } else {
          console.log('ℹ️ Product found by global lookup for productId:', productId, 'assignto_id:', globalQuery.rows[0].assignto_id);
          productQuery.rows.push(globalQuery.rows[0]);
        }
      } catch (gErr) {
        console.error('❌ Global product lookup error:', gErr.message);
        return res.status(500).json({ message: 'Server error' });
      }
    }

    const row = productQuery.rows[0];
    
    // Calculate warranty dates (default 25 years from installation)
    const installationDate = row.file_saved_at ? new Date(row.file_saved_at) : new Date();
    const warrantyEndDate = new Date(installationDate);
    warrantyEndDate.setFullYear(warrantyEndDate.getFullYear() + 25);

    const product = {
      id: row.id,
      productId: row.barcode_data || `PROD-${row.id}`,
      productImage: row.barcode_path || null,
      brand: row.company || row.company_name || 'Unknown Brand',
      model: row.product_name || 'Unknown Model',
      wattage: row.wattage ? `${row.wattage} Wp` : null,
      quantity: 1,
      warranty: '25 year',
      warrantyStart: installationDate.toISOString().split('T')[0],
      warrantyEnd: warrantyEndDate.toISOString().split('T')[0],
      price: null, // Price not stored in barcodeimage table
      tax: null,
      taxPercent: 18,
    };

    res.json({ product });
  } catch (error) {
    console.error('Get product details error:', error);
    res.status(500).json({ 
      message: 'Server error',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined 
    });
  }
});

// Download invoice
router.get('/products/:productId/invoice', authenticate, async (req, res) => {
  try {
    const authUserId = getAuthUserId(req);
    const productId = req.params.productId;

    if (!authUserId) {
      return res.status(401).json({ message: 'Could not identify user' });
    }

    // Verify product belongs to user
    const productQuery = await pool.query(
      `SELECT id, barcode_data
       FROM detect_barcodes_barcodeimage
       WHERE (barcode_data = $1 OR id::text = $1)
         AND assignto_id = $2
       LIMIT 1`,
      [productId, authUserId]
    );

    if (productQuery.rows.length === 0) {
      return res.status(404).json({ message: 'Product not found' });
    }

    // For now, return a placeholder message
    // In production, generate actual PDF invoice
    res.status(501).json({ 
      message: 'Invoice generation not yet implemented. Please contact support for invoice.' 
    });
  } catch (error) {
    console.error('Download invoice error:', error);
    res.status(500).json({ 
      message: 'Server error',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined 
    });
  }
});

module.exports = router;
