// Quotation list interactive behavior
(function(){
  function getCSRFToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return meta.content;
    const name = 'csrftoken';
    const cookies = document.cookie.split(';').map(c=>c.trim());
    for (const c of cookies) {
      if (c.startsWith(name + '=')) return decodeURIComponent(c.split('=')[1]);
    }
    return '';
  }

  function applyFilters(searchInput, filterType, filterProject) {
    const text = (searchInput && searchInput.value || '').trim().toLowerCase();
    const type = (filterType && filterType.value || '').toLowerCase();
    const project = (filterProject && filterProject.value || '').toLowerCase();
    document.querySelectorAll('#quotationTableBody tr').forEach(r => {
      const cells = r.textContent.toLowerCase();
      const okText = !text || cells.indexOf(text) !== -1;
      // prefer data attributes for exactness
      const rowType = (r.dataset.consumerType || '').toLowerCase();
      const rowProject = (r.dataset.projectType || '').toLowerCase();
      const okType = !type || rowType.indexOf(type) !== -1 || cells.indexOf(type) !== -1;
      const okProject = !project || rowProject.indexOf(project) !== -1 || cells.indexOf(project) !== -1;
      r.style.display = (okText && okType && okProject) ? '' : 'none';
    });
  }

  document.addEventListener('DOMContentLoaded', function(){
    const searchInput = document.getElementById('qSearch');
    const filterType = document.getElementById('filterType');
    const filterProject = document.getElementById('filterProject');
    const applyBtn = document.getElementById('applyFilters');

    if (applyBtn) applyBtn.addEventListener('click', () => applyFilters(searchInput, filterType, filterProject));
    const clearBtn = document.getElementById('clearFilters');
    if (clearBtn) {
      clearBtn.addEventListener('click', function(){
        if (searchInput) searchInput.value = '';
        if (filterType) filterType.value = '';
        if (filterProject) filterProject.value = '';
        applyFilters(searchInput, filterType, filterProject);
      });
    }
    if (searchInput) searchInput.addEventListener('input', () => applyFilters(searchInput, filterType, filterProject));
    if (filterType) filterType.addEventListener('change', () => applyFilters(searchInput, filterType, filterProject));
    if (filterProject) filterProject.addEventListener('change', () => applyFilters(searchInput, filterType, filterProject));

    // Export CSV
    const exportBtn = document.getElementById('exportCsv');
    if (exportBtn) exportBtn.addEventListener('click', function(e){
      e.preventDefault();
      const rows = [['Quotation No','Consumer','Type','Project','Capacity(kW)','Date','Final Amount','Status']];
      document.querySelectorAll('#quotationTableBody tr').forEach(tr => {
        if (tr.style.display === 'none') return;
        const cols = Array.from(tr.children);
        rows.push([
          cols[0]?.innerText.trim(), // Quotation No
          cols[1]?.innerText.trim(), // Consumer
          cols[2]?.innerText.trim(), // Type
          cols[3]?.innerText.trim(), // Project
          cols[4]?.innerText.trim(), // Capacity
          cols[5]?.innerText.trim(), // Date
          cols[6]?.innerText.trim(), // Final Amount
          cols[7]?.innerText.trim()  // Status
        ]);
      });
      const csv = rows.map(r => r.map(c => '"' + String(c).replace(/"/g,'""') + '"').join(',')).join('\n');
      const blob = new Blob([csv], {type:'text/csv'});
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'quotations_export.csv';
      document.body.appendChild(a); a.click(); a.remove();
    });

    // Convert modal flow
    let convertTargetId = null;
    const convertModalEl = document.getElementById('convertModal');
    const convertModal = convertModalEl ? new bootstrap.Modal(convertModalEl) : null;
    const convertText = document.getElementById('convertModalText');
    const convertError = document.getElementById('convertError');
    const confirmConvertBtn = document.getElementById('confirmConvert');

    // Click handler for convert buttons.
    document.querySelectorAll('.convert-btn, .convert-consumer-btn').forEach(btn => {
      btn.addEventListener('click', function(){
        convertTargetId = this.dataset.id;
        if (convertText) convertText.textContent = `Convert quotation #${convertTargetId} to a consumer?`;
        if (convertError) convertError.classList.add('d-none');
        if (convertModal) {
          convertModal.show();
        } else {
          // No modal present in template — directly start conversion flow
          doConvert(convertTargetId);
        }
      });
    });

    // Shared conversion function used by confirm button or direct flow
    async function doConvert(quotationId) {
      if (!quotationId) return;
      if (confirmConvertBtn) confirmConvertBtn.disabled = true;
      try {
        const resp = await fetch('/quotation/get-quotation-details/' + encodeURIComponent(quotationId) + '/');
        if (!resp.ok) throw new Error('Failed to fetch quotation');
        const data = await resp.json();
        // Store in session (best-effort)
        fetch('/quotation/store-quotation-data/', {
          method:'POST',
          headers:{'Content-Type':'application/json','X-CSRFToken': getCSRFToken()},
          body: JSON.stringify({data: data, quotation_id: quotationId})
        }).catch(()=>{});
        const map = {
          'Residential': '/customer/Cust_emp/',
          'Commercial': '/customer/Comm_Cust/',
          'Industrial': '/customer/Comp_Cust/',
          'Government': '/customer/Govt_Cust/'
        };
        const dest = map[data.consumer_type] || '/customer/Cust_emp/';
        const url = new URL(dest, window.location.origin);
        url.searchParams.set('from_quotation','1');
        url.searchParams.set('quotation_id', quotationId);
        // Append quotation details so customer pages can pre-fill from GET params
        const fields = ['consumer_type','project_type','plant_capacity','phase','consumer_no','consumer_full_name','first_name','middle_name','last_name','address','city','state','email','phone','po_order_no','po_date','comp_name'];
        fields.forEach(k => {
          if (data[k] !== undefined && data[k] !== null) {
            url.searchParams.set(k, String(data[k]));
          }
        });
        window.location.href = url.toString();
      } catch (err) {
        if (convertError) {
          convertError.textContent = (err.message || 'Conversion failed.');
          convertError.classList.remove('d-none');
        }
        console.error(err);
      } finally {
        if (confirmConvertBtn) confirmConvertBtn.disabled = false;
      }
    }

    if (confirmConvertBtn) {
      confirmConvertBtn.addEventListener('click', function(){
        if (!convertTargetId) return;
        doConvert(convertTargetId);
      });
    }

    // Confirm modal: only Save submits; closing (X / Cancel / backdrop) must not POST or change the list.
    const confirmForm = document.getElementById('confirmForm');
    if (confirmForm) {
      confirmForm.addEventListener('submit', function(e){
        e.preventDefault();
        const qId = window.__confirmQuotationId || null;
        if (!qId) {
          return;
        }
        fetch(`/quotation/confirm/${qId}/`, {
          method: 'POST',
          body: new FormData(this),
          headers: { 'X-CSRFToken': getCSRFToken() }
        }).then(function(response) {
          if (response.ok) {
            window.location.reload();
          }
        }).catch(function() { /* keep modal open; user can retry */ });
      });
    }
    const confirmModalEl = document.getElementById('confirmModal');
    if (confirmModalEl) {
      confirmModalEl.addEventListener('show.bs.modal', function(e){
        const b = e.relatedTarget;
        if (!b || !b.dataset || !b.dataset.id) {
          return;
        }
        window.__confirmQuotationId = b.dataset.id;
        const map = {
          'm_name': 'name',
          'm_capacity': 'capacity',
          'm_no': 'no',
          'm_date': 'date',
          'm_amount': 'amount'
        };
        Object.keys(map).forEach(function(k) {
          const el = document.getElementById(k);
          if (el) el.innerText = b.dataset[map[k]] || '';
        });
        const paymentModeEl = document.getElementById('paymentMode');
        const hybridBoxEl = document.getElementById('hybridBox');
        if (paymentModeEl && hybridBoxEl) {
          hybridBoxEl.classList.toggle('d-none', paymentModeEl.value !== 'Hybrid');
        }
      });
      confirmModalEl.addEventListener('hidden.bs.modal', function(){
        window.__confirmQuotationId = null;
        if (confirmForm) {
          confirmForm.reset();
        }
        const hybridBoxEl = document.getElementById('hybridBox');
        if (hybridBoxEl) hybridBoxEl.classList.add('d-none');
      });
    }
    // Toggle hybrid sub-field when payment mode changes (attach once)
    const paymentModeEl = document.getElementById('paymentMode');
    const hybridBoxEl = document.getElementById('hybridBox');
    if (paymentModeEl) {
      paymentModeEl.addEventListener('change', function(){
        if (hybridBoxEl) hybridBoxEl.classList.toggle('d-none', this.value !== 'Hybrid');
      });
    }

    // Toggle details helper
    window.toggleDetails = function(baseNo, el){
      const rows = document.querySelectorAll('.base-' + baseNo);
      const expanded = el.dataset.expanded === "1";
      rows.forEach(row => {
        if (row.dataset.latest === "0") {
          row.style.display = expanded ? "none" : "";
          row.classList.toggle("previous-quotation", !expanded);
        }
      });
      if (expanded) {
        el.innerText = el.dataset.label || "Details";
        el.dataset.expanded = "0";
      } else {
        el.innerText = "Hide Details";
        el.dataset.expanded = "1";
      }
    };

    // small utility to show success banner
    window.showSuccessBanner = function(message, timeout=1200, cb){
      let b = document.getElementById('success-banner');
      if (!b) {
        b = document.createElement('div'); b.id = 'success-banner'; b.className='success-banner';
        document.body.appendChild(b);
      }
      b.textContent = message; b.style.display = 'block';
      setTimeout(()=>{ b.style.display='none'; if (cb) cb(); }, timeout);
    };
  });
})();
