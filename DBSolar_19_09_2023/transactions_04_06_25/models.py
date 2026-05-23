
from django.contrib.auth.models import User
from django.db import models
from django.apps import apps
from django.db import models

from django.db import models

from customer.models import Customer
from inventory.models import Stock
from product.models import Category, Unit


# contains suppliers
class Supplier(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150, unique=True)
    phone = models.CharField(max_length=12, unique=True)
    address = models.CharField(max_length=200)
    email = models.EmailField(max_length=254, unique=True)
    gstin = models.CharField(max_length=15, unique=True)
    is_deleted = models.BooleanField(default=False)
    supplier_id = models.CharField(max_length=20, unique=True, blank=True)  # Custom ID field
    contact_person = models.CharField(max_length=100, null=True)
    # category = models.ForeignKey(Category, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='product_suppliers')
    city = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=50, null=True)
    post_code = models.CharField(max_length=10, null=True)
    status = models.BooleanField(default=True, null=True)

    def save(self, *args, **kwargs):
        # Check if the supplier exists and retrieve the previous category
        if self.pk:
            previous_supplier = Supplier.objects.get(pk=self.pk)
            previous_category = previous_supplier.category
        else:
            previous_category = None

        # Generate supplier_id if it's a new record or if the category has changed
        if not self.supplier_id or self.category != previous_category:
            # Loop until a unique supplier_id is generated
            unique_supplier_id = False
            suffix = 101
            while not unique_supplier_id:
                last_supplier = Supplier.objects.filter(category=self.category).order_by('id').last()
                if last_supplier:
                    last_id = int(last_supplier.supplier_id.split('-')[1])
                    proposed_supplier_id = f"{self.category.short_name.upper()}-{last_id + 1}"
                else:
                    proposed_supplier_id = f"{self.category.short_name.upper()}-{suffix}"

                # Check if this supplier_id already exists
                if not Supplier.objects.filter(supplier_id=proposed_supplier_id).exists():
                    self.supplier_id = proposed_supplier_id
                    unique_supplier_id = True
                else:
                    suffix += 1

        super(Supplier, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


# contains suppliers
class Vendor(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150, unique=True)
    phone = models.CharField(max_length=12, unique=True)
    address = models.CharField(max_length=200)
    email = models.EmailField(max_length=254, unique=True)
    # gstin = models.CharField(max_length=15, unique=True)
    gstin = models.CharField(max_length=15, blank=True, null=True,
                             unique=True)  # Allow NULL values while keeping it unique
    is_deleted = models.BooleanField(default=False)
    vendor_id = models.CharField(max_length=20, unique=True, blank=True)  # Custom ID field
    contact_person = models.CharField(max_length=100, null=True)
    # category = models.ForeignKey(Category, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='product_vendor')
    city = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=50, null=True)
    post_code = models.CharField(max_length=10, null=True)
    status = models.BooleanField(default=True, null=True)

    def save(self, *args, **kwargs):
        # Check if the vendor exists and retrieve the previous category
        if self.pk:
            previous_vendor = Vendor.objects.get(pk=self.pk)
            previous_category = previous_vendor.category
        else:
            previous_category = None

        # Generate supplier_id if it's a new record or if the category has changed
        if not self.vendor_id or self.category != previous_category:
            # Loop until a unique supplier_id is generated
            unique_vendor_id = False
            suffix = 101
            prefix = (self.category.short_name or "").upper()
            if prefix in {"OTHER", "OTHERS"}:
                prefix = "DLR"
            while not unique_vendor_id:
                last_vendor = Vendor.objects.filter(category=self.category).order_by('id').last()
                if last_vendor:
                    last_id = int(last_vendor.vendor_id.split('-')[1])
                    proposed_vendor_id = f"{prefix}-{last_id + 1}"
                else:
                    proposed_vendor_id = f"{prefix}-{suffix}"

                # Check if this supplier_id already exists
                if not Vendor.objects.filter(vendor_id=proposed_vendor_id).exists():
                    self.vendor_id = proposed_vendor_id
                    unique_vendor_id = True
                else:
                    suffix += 1

        super(Vendor, self).save(*args, **kwargs)

    def __str__(self):
        return self.name



# contains the purchase bills made
class PurchaseBill(models.Model):
    billno = models.AutoField(primary_key=True)
    time = models.DateTimeField(auto_now=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchasesupplier')

    def __str__(self):
        return "Bill no: " + str(self.billno)

    def get_items_list(self):
        return PurchaseItem.objects.filter(billno=self)

    def get_total_price(self):
        purchaseitems = PurchaseItem.objects.filter(billno=self)
        total = 0
        for item in purchaseitems:
            total += item.totalprice
        return total

    def get_final_amount(self):
        try:
            # Assuming there's only one PurchaseBillDetails for each PurchaseBill
            purchase_details = PurchaseBillDetails.objects.get(billno=self)
            return purchase_details.final_amount
        except PurchaseBillDetails.DoesNotExist:
            return 0  # or handle it as you see fit

    def get_po(self):
        # return self.purchasebilldetails.eway  # Ensure reverse relation exists
        purchase_po = PurchaseBillDetails.objects.get(billno=self)
        return purchase_po.po

    def get_serialNo_list(self):
        return PurchaseSerial.objects.filter(billno=self)


# contains the purchase stocks made
class PurchaseItem(models.Model):
    billno = models.ForeignKey(PurchaseBill, on_delete=models.CASCADE, related_name='purchasebillno')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='purchaseitem')
    quantity = models.IntegerField(default=1)
    # perprice = models.IntegerField(default=1)
    perprice = models.DecimalField(max_digits=10, decimal_places=3, null=True)  # Store final amount
    totalprice = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Store final amount
    purchase = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='purchaseitem_purchased_products', null=True)

    def __str__(self):
        return "Bill no: " + str(self.billno.billno) + ", Item = " + self.stock.name


# contains the other details in the purchases bill
class PurchaseBillDetails(models.Model):
    billno = models.ForeignKey(PurchaseBill, on_delete=models.CASCADE, related_name='purchasedetailsbillno')

    eway = models.CharField(max_length=50, blank=True, null=True)
    veh = models.CharField(max_length=50, blank=True, null=True)
    destination = models.CharField(max_length=50, blank=True, null=True)
    po = models.CharField(max_length=50, blank=True, null=True)

    cgst = models.CharField(max_length=50, blank=True, null=True)
    sgst = models.CharField(max_length=50, blank=True, null=True)
    igst = models.CharField(max_length=50, blank=True, null=True)
    cess = models.CharField(max_length=50, blank=True, null=True)
    tcs = models.CharField(max_length=50, blank=True, null=True)
    total = models.CharField(max_length=50, blank=True, null=True)
    gst_value = models.CharField(max_length=50, blank=True, null=True)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Store total GST amount
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Store final amount
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Store final amount
    round_off = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Store final amount
    delivery_charges = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Store final amount

    def __str__(self):
        return "Bill no: " + str(self.billno.billno)



class FinalSale(models.Model):
    billno = models.AutoField(primary_key=True)
    time = models.DateTimeField(null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='final_sales', null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='final_sales_vendor', null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    update_time = models.DateTimeField(null=True)
    # return_bill = models.BooleanField(default=False, unique=True)
    return_bill = models.BooleanField(default=False)
    return_date = models.DateTimeField(null=True)

    def __str__(self):
        return f"Final Bill No: {self.billno}"

    @property
    def get_items_list(self):
        return self.final_sale_items.all()  # Fetch all related FinalSaleItem objects

    def get_final_amount(self):
        try:
            # Assuming there's only one PurchaseBillDetails for each PurchaseBill
            final_bill_details = FinalBillDetails.objects.get(billno=self)
            return final_bill_details.final_amount
        except FinalBillDetails.DoesNotExist:
            return 0  # or handle it as you see fit


class FinalSaleItem(models.Model):
    final_bill = models.ForeignKey(FinalSale, on_delete=models.CASCADE, related_name='final_sale_items')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='final_sale_stock')
    total_quantity = models.IntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, null=True)

    r_quantity = models.IntegerField(null=True)
    final_quantity = models.IntegerField(null=True)


    def __str__(self):
        return f"Final Bill No: {self.final_bill.billno}, Stock: {self.stock.name}"




# contains the other details in the sales bill
class FinalBillDetails(models.Model):
    billno = models.ForeignKey(FinalSale, on_delete=models.CASCADE, related_name='finaldetailsbillno')

    eway = models.CharField(max_length=50, blank=True, null=True)
    veh = models.CharField(max_length=50, blank=True, null=True)
    destination = models.CharField(max_length=50, blank=True, null=True)
    po = models.CharField(max_length=50, blank=True, null=True)

    cgst = models.CharField(max_length=50, blank=True, null=True)
    sgst = models.CharField(max_length=50, blank=True, null=True)
    igst = models.CharField(max_length=50, blank=True, null=True)
    cess = models.CharField(max_length=50, blank=True, null=True)
    tcs = models.CharField(max_length=50, blank=True, null=True)
    total = models.CharField(max_length=50, blank=True, null=True)

    gst_value = models.CharField(max_length=50, blank=True, null=True)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Store total GST amount
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Store final amount
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Store final amount
    round_off = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Store final amount


    def __str__(self):
        return "Final Bill no: " + str(self.billno.billno)





class ReturnSale(models.Model):
    billno = models.AutoField(primary_key=True)
    time = models.DateTimeField(null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='return_sales', blank=True, null=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='return_vendor', blank=True, null=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    update_time = models.DateTimeField(null=True)
    final_bill = models.ForeignKey(FinalSale, on_delete=models.CASCADE, related_name='return_sales', null=True, blank=True)
    # return_bill = models.BooleanField(default=False, unique=True)
    # update_date = models.DateTimeField(null=True)


    def __str__(self):
        return f"Return Bill No: {self.billno}"

    @property
    def get_items_list(self):
        return self.return_sale_items.all()  # Fetch all related FinalSaleItem objects

    def get_final_amount(self):
        try:
            # Assuming there's only one PurchaseBillDetails for each PurchaseBill
            return_bill_details = ReturnBillDetails.objects.get(billno=self)
            return return_bill_details.final_amount
        except ReturnBillDetails.DoesNotExist:
            return 0  # or handle it as you see fit


class ReturnSaleItem(models.Model):
    # final_bill = models.ForeignKey(FinalSale, on_delete=models.CASCADE, related_name='final_sale_items')
    return_bill = models.ForeignKey(ReturnSale, on_delete=models.CASCADE, related_name='return_sale_items')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='return_sale_stock')
    total_quantity = models.IntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    final_bill = models.ForeignKey(FinalSale, on_delete=models.CASCADE, related_name='return_finalbill_items', null=True, blank=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, null=True)

    r_quantity = models.IntegerField(null=True)
    final_quantity = models.IntegerField(null=True)


    def __str__(self):
        return f"Return Bill No: {self.return_bill.billno}, Stock: {self.stock.name}"




# contains the other details in the sales bill
class ReturnBillDetails(models.Model):
    billno = models.ForeignKey(ReturnSale, on_delete=models.CASCADE, related_name='returndetailsbillno')

    eway = models.CharField(max_length=50, blank=True, null=True)
    veh = models.CharField(max_length=50, blank=True, null=True)
    destination = models.CharField(max_length=50, blank=True, null=True)
    po = models.CharField(max_length=50, blank=True, null=True)

    cgst = models.CharField(max_length=50, blank=True, null=True)
    sgst = models.CharField(max_length=50, blank=True, null=True)
    igst = models.CharField(max_length=50, blank=True, null=True)
    cess = models.CharField(max_length=50, blank=True, null=True)
    tcs = models.CharField(max_length=50, blank=True, null=True)
    total = models.CharField(max_length=50, blank=True, null=True)

    gst_value = models.CharField(max_length=50, blank=True, null=True)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Store total GST amount
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Store final amount
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Store final amount
    round_off = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Store final amount
    final_bill = models.ForeignKey(FinalSale, on_delete=models.CASCADE, related_name='return_bill_details', null=True, blank=True)


    def __str__(self):
        return "Return Bill no: " + str(self.billno.billno)



# contains the sale bills made
class SaleBill(models.Model):
    billno = models.AutoField(primary_key=True)
    time = models.DateTimeField(null=True)
    Cust_id = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='salescustomer', null=True, blank=True)
    Vend_id = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='salesvendor', null=True, blank=True)
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=12)
    address = models.CharField(max_length=200)
    email = models.EmailField(max_length=254)
    gstin = models.CharField(max_length=15)
    # final_salebillno = models.IntegerField(null=True, blank=True)  # New field added
    final_salebill = models.ForeignKey(FinalSale, on_delete=models.CASCADE, related_name='sale_bills', null=True, blank=True)
    # final_salebill = models.ForeignKey(FinalSale, on_delete=models.SET_NULL, null=True, blank=True)
    update_time = models.DateTimeField(null=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return "Bill no: " + str(self.billno)

    def get_items_list(self):
        return SaleItem.objects.filter(billno=self)

    def get_total_price(self):
        saleitems = SaleItem.objects.filter(billno=self)
        total = 0
        for item in saleitems:
            total += item.totalprice
        return total
    def get_final_amount(self):
        try:
            # Assuming there's only one PurchaseBillDetails for each PurchaseBill
            sale_details = SaleBillDetails.objects.get(billno=self)
            return sale_details.final_amount
        except SaleBillDetails.DoesNotExist:
            return 0  # or handle it as you see fit





class PurchaseSerial(models.Model):
    billno = models.ForeignKey(PurchaseBill, on_delete=models.CASCADE, related_name='purchase_serials')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='purchase_serials')
    purchase = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='purchaseserial_purchases')
    # billno = models.ForeignKey(PurchaseBill, on_delete=models.CASCADE, related_name='purchasebillno')
    # stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='purchaseitem')
    serialNo = models.CharField(max_length=50, blank=True, null=True)
    item = models.ForeignKey(PurchaseItem, on_delete=models.CASCADE, related_name='purchaseserial_set', null=True)
    sales_billno = models.ForeignKey(SaleBill, on_delete=models.CASCADE, related_name='sale_bill', null=True)
    final_salebill = models.ForeignKey(FinalSale, on_delete=models.CASCADE, related_name='sale_bills1', null=True, blank=True)
    return_bill = models.ForeignKey(ReturnSale, on_delete=models.CASCADE, related_name='return_bills', null=True,
                                       blank=True)

    # purchase = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='purchaseitem_purchased_products', null=True)

    def __str__(self):
        return "Bill no: " + str(self.billno.billno) + ", Item = " + self.stock.name


# contains the sale stocks made
class SaleItem(models.Model):
    billno = models.ForeignKey(SaleBill, on_delete=models.CASCADE, related_name='salebillno')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='saleitem')
    quantity = models.IntegerField(default=1)
    perprice = models.IntegerField(default=1)
    totalprice = models.IntegerField(default=1)
    sale = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='saleitem_saled_products',
                                 null=True)

    r_quantity = models.IntegerField(null=True)
    total_quantity = models.IntegerField(null=True)

    def __str__(self):
        return "Bill no: " + str(self.billno.billno) + ", Item = " + self.stock.name


# contains the other details in the sales bill
class SaleBillDetails(models.Model):
    billno = models.ForeignKey(SaleBill, on_delete=models.CASCADE, related_name='saledetailsbillno')

    eway = models.CharField(max_length=50, blank=True, null=True)
    veh = models.CharField(max_length=50, blank=True, null=True)
    destination = models.CharField(max_length=50, blank=True, null=True)
    po = models.CharField(max_length=50, blank=True, null=True)

    cgst = models.CharField(max_length=50, blank=True, null=True)
    sgst = models.CharField(max_length=50, blank=True, null=True)
    igst = models.CharField(max_length=50, blank=True, null=True)
    cess = models.CharField(max_length=50, blank=True, null=True)
    tcs = models.CharField(max_length=50, blank=True, null=True)
    total = models.CharField(max_length=50, blank=True, null=True)

    gst_value = models.CharField(max_length=50, blank=True, null=True)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Store total GST amount
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Store final amount
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Store final amount
    round_off = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Store final amount


    def __str__(self):
        return "Bill no: " + str(self.billno.billno)


#
# class FinalSale(models.Model):
#     name = models.CharField(max_length=150)
#     total_quantity = models.IntegerField(default=0)
#     total_price = models.DecimalField(max_digits=10, decimal_places=2)
#     items = models.ManyToManyField(SaleItem, related_name='finalsale_items')
#
#     def __str__(self):
#         return f"Final Sale: {self.name}"


