-- Fix boolean fields in product app tables
-- Convert bit varying to boolean type

-- Fix product_category.status
ALTER TABLE product_category 
ALTER COLUMN status TYPE boolean 
USING CASE 
    WHEN status::text = '1' THEN true 
    WHEN status::text = '0' THEN false 
    WHEN status IS NULL THEN NULL 
    ELSE status::text::boolean 
END;

-- Fix product_subcategory.status  
ALTER TABLE product_subcategory 
ALTER COLUMN status TYPE boolean 
USING CASE 
    WHEN status::text = '1' THEN true 
    WHEN status::text = '0' THEN false 
    WHEN status IS NULL THEN NULL 
    ELSE status::text::boolean 
END;

-- Fix product_product.status
ALTER TABLE product_product 
ALTER COLUMN status TYPE boolean 
USING CASE 
    WHEN status::text = '1' THEN true 
    WHEN status::text = '0' THEN false 
    WHEN status IS NULL THEN NULL 
    ELSE status::text::boolean 
END;

-- Fix product_brand.status (if it exists)
ALTER TABLE product_brand 
ALTER COLUMN status TYPE boolean 
USING CASE 
    WHEN status::text = '1' THEN true 
    WHEN status::text = '0' THEN false 
    WHEN status IS NULL THEN NULL 
    ELSE status::text::boolean 
END;

-- Verify the changes
SELECT 
    table_name, 
    column_name, 
    data_type 
FROM information_schema.columns 
WHERE table_name IN ('product_category', 'product_subcategory', 'product_product', 'product_brand')
    AND column_name = 'status'
ORDER BY table_name;

