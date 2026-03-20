# ============================================================
# SYNC ENGINE v3 - Map API response -> DB
# ============================================================

from datetime import datetime

def _dt(val):
    if val is None: return None
    if isinstance(val, datetime): return val
    if isinstance(val, str):
        val = val.strip()
        if not val: return None
        for fmt in ("%Y-%m-%dT%H:%M:%S","%Y-%m-%dT%H:%M:%S.%f","%Y-%m-%d %H:%M:%S","%Y-%m-%d"):
            try: return datetime.strptime(val, fmt)
            except ValueError: pass
        return None
    return None

def _dt6(val):
    if val is None: return None
    if isinstance(val, datetime): return val
    if isinstance(val, str):
        val = val.strip()
        if not val: return None
        for fmt in ("%Y-%m-%dT%H:%M:%S.%f","%Y-%m-%dT%H:%M:%S"):
            try: return datetime.strptime(val, fmt)
            except ValueError: pass
        return None
    return None

def _date(val):
    if val is None: return None
    if isinstance(val, str):
        val = val.strip()
        if not val: return None
        try: return datetime.strptime(val[:10], "%Y-%m-%d").date()
        except: return None
    if hasattr(val, "date"): return val.date()
    return None

def _int(val):
    if val is None: return None
    try: return int(val)
    except: return None

def _float(val):
    if val is None: return None
    try: return float(val)
    except: return None

def _dec2(val):
    f = _float(val)
    if f is not None: return round(f, 2)
    return None

def _str(val):
    if val is None: return None
    if isinstance(val, str): return val.strip() or None
    return str(val) if val is not None else None

def _get_nested(row, path, default=None):
    keys = path.split(".")
    val = row
    for k in keys:
        if val is None:
            return default
        if isinstance(val, dict):
            val = val.get(k)
        elif isinstance(val, list):
            try:
                idx = int(k)
                val = val[idx] if 0 <= idx < len(val) else None
            except ValueError:
                return default
        else:
            return default
    return val

FIELD_MAPS = {
    "products": {
        "table": "products", "primary_key": "id",
        "fields": {
            "product_id": "id", "shop_id": "shop_id",
            "product.display_id": "display_id", "product.name": "name",
            "product.image": "image", "product.is_published": "is_published",
            "product.note": "note", "product.note_product": "note_product",
            "product.measure_group_id": "measure_group_id",
            "product.created_at": "created_at",
            "product.updated_at": "updated_at",
            "product.custom_id": "custom_id",
            "product.type": "type",
            "product.brand_id": "brand_id",
            "product.is_composite": "is_composite",
        },
        "transforms": {
            "shop_id": _int, "product.is_published": _int,
            "product.measure_group_id": _int,
            "product.created_at": _dt, "product.updated_at": _dt,
            "product.brand_id": _int,
            "product.is_composite": _int,
        },
    },
    "variations": {
        "table": "product_variations", "primary_key": "id",
        "fields": {
            "id": "id", "product_id": "product_id", "shop_id": "shop_id",
            "name": "name", "display_id": "display_id", "barcode": "barcode",
            "retail_price": "retail_price",
            "average_imported_price": "average_imported_price",
            "price_at_counter": "price_at_counter",
            "last_imported_price": "last_imported_price",
            "retail_price_after_discount": "retail_price_after_discount",
            "total_purchase_price": "total_purchase_price",
            "wholesale_price": "wholesale_price",
            "tax_rate": "tax_rate", "weight": "weight",
            "is_hidden": "is_hidden", "is_locked": "is_locked",
            "is_composite": "is_composite", "is_removed": "is_removed",
            "is_sell_negative_variation": "is_sell_negative_variation",
            "remain_quantity": "remain_quantity",
            "inserted_at": "inserted_at",
        },
        "transforms": {
            "shop_id": _int, "retail_price": _dec2,
            "average_imported_price": _dec2, "price_at_counter": _dec2,
            "last_imported_price": _dec2, "retail_price_after_discount": _dec2,
            "total_purchase_price": _dec2, "wholesale_price": _dec2,
            "tax_rate": _float, "weight": _float,
            "is_hidden": _int, "is_locked": _int,
            "is_composite": _int, "is_removed": _int,
            "is_sell_negative_variation": _int,
            "remain_quantity": _int,
            "inserted_at": _dt6,
        },
    },
    "orders": {
        "table": "orders", "primary_key": "id",
        "fields": {
            "id": "id", "shop_id": "shop_id",
            "page.id": "page_id",
            "order_code": "order_code",
            "conversation_id": "conversation_id", "post_id": "post_id", "ad_id": "ad_id",
            "creator_id": "creator_id", "assigning_seller_id": "assigning_seller_id",
            "assigning_care_id": "assigning_care_id", "marketer_id": "marketer_id",
            "customer.id": "customer_id", "warehouse_id": "warehouse_id",
            "status": "status", "sub_status": "sub_status", "status_name": "status_name",
            "bill_full_name": "bill_full_name", "bill_phone_number": "bill_phone_number",
            "bill_email": "bill_email",
            "shipping_address.full_name": "shipping_full_name",
            "shipping_address.phone_number": "shipping_phone_number",
            "shipping_address.address": "shipping_address",
            "shipping_address.full_address": "shipping_full_address",
            "shipping_address.province_id": "shipping_province_id",
            "shipping_address.province_name": "shipping_province_name",
            "shipping_address.district_id": "shipping_district_id",
            "shipping_address.district_name": "shipping_district_name",
            "shipping_address.commune_id": "shipping_commune_id",
            "shipping_address.commune_name": "shipping_commune_name",
            "shipping_address.country_code": "shipping_country_code",
            "shipping_address.post_code": "shipping_post_code",
            "order_sources": "order_sources", "order_sources_name": "order_sources_name",
            "ads_source": "ads_source",
            "p_utm_source": "p_utm_source", "p_utm_medium": "p_utm_medium",
            "p_utm_campaign": "p_utm_campaign", "p_utm_content": "p_utm_content",
            "p_utm_term": "p_utm_term", "p_utm_id": "p_utm_id",
            "is_livestream": "is_livestream", "is_live_shopping": "is_live_shopping",
            "total_price": "total_price", "total_price_after_sub_discount": "total_price_after_sub_discount",
            "total_discount": "total_discount", "shipping_fee": "shipping_fee",
            "surcharge": "surcharge", "tax": "tax", "cod": "cod",
            "money_to_collect": "money_to_collect", "prepaid": "prepaid",
            "cash": "cash", "transfer_money": "transfer_money",
            "charged_by_momo": "charged_by_momo", "charged_by_card": "charged_by_card",
            "charged_by_qrpay": "charged_by_qrpay",
            "exchange_payment": "exchange_payment", "exchange_value": "exchange_value",
            "buyer_total_amount": "buyer_total_amount", "fee_marketplace": "fee_marketplace",
            "levera_point": "levera_point", "partner": "partner",
            "tracking_link": "tracking_link", "time_send_partner": "time_send_partner",
            "estimate_delivery_date": "estimate_delivery_date",
            "returned_reason": "returned_reason", "returned_reason_name": "returned_reason_name",
            "note": "note", "note_print": "note_print", "link": "link",
            "time_assign_seller": "time_assign_seller", "time_assign_care": "time_assign_care",
            "customer_referral_code": "customer_referral_code",
            "is_smc": "is_smc", "customer_pay_fee": "customer_pay_fee",
            "received_at_shop": "received_at_shop", "partner_fee": "partner_fee",
            "return_fee": "return_fee",
            "is_free_shipping": "is_free_shipping", "is_exchange_order": "is_exchange_order",
            "is_calculation_tax": "is_calculation_tax",
            "inserted_at": "inserted_at", "updated_at": "updated_at",
        },
        "transforms": {
            "shop_id": _int, "status": _int,
            "total_price": _float, "total_price_after_sub_discount": _dec2,
            "total_discount": _dec2, "shipping_fee": _dec2, "surcharge": _dec2,
            "tax": _dec2, "cod": _float, "money_to_collect": _dec2, "prepaid": _dec2,
            "cash": _dec2, "transfer_money": _dec2, "charged_by_momo": _dec2,
            "charged_by_card": _dec2, "charged_by_qrpay": _dec2,
            "exchange_payment": _dec2, "exchange_value": _dec2,
            "buyer_total_amount": _dec2, "fee_marketplace": _float,
            "levera_point": _int, "partner_fee": _dec2, "return_fee": _float,
            "is_livestream": _int, "is_live_shopping": _int,
            "is_smc": _int, "customer_pay_fee": _int, "received_at_shop": _int,
            "is_free_shipping": _int, "is_exchange_order": _int, "is_calculation_tax": _int,
            "inserted_at": _dt, "updated_at": _dt,
            "time_send_partner": _dt, "estimate_delivery_date": _dt,
            "time_assign_seller": _dt, "time_assign_care": _dt,
            "shipping_address.phone_number": _str,
            "shipping_address.province_id": _str, "shipping_address.district_id": _str,
            "shipping_address.commune_id": _str, "shipping_address.country_code": _str,
            "shipping_address.post_code": _str,
        },
    },
    "customers": {
        "table": "customers", "primary_key": "id",
        "fields": {
            "id": "id", "shop_id": "shop_id", "name": "name", "gender": "gender",
            "date_of_birth": "date_of_birth", "fb_id": "fb_id",
            "referral_code": "referral_code",
            "is_discount_by_level": "is_discount_by_level", "reward_point": "reward_point",
            "used_reward_point": "used_reward_point", "current_debts": "current_debts",
            "level": "level", "is_block": "is_block",
            "order_count": "order_count", "succeed_order_count": "succeed_order_count",
            "returned_order_count": "returned_order_count", "purchased_amount": "purchased_amount",
            "last_order_at": "last_order_at", "assigned_user_id": "assigned_user_id",
            "creator_id": "creator_id", "inserted_at": "inserted_at",
            "updated_at": "updated_at",
            "phone_numbers.0": "phone_number", "emails.0": "email",
            "count_referrals": "count_referrals",
        },
        "transforms": {
            "shop_id": _int, "date_of_birth": _date, "reward_point": _int,
            "used_reward_point": _int, "current_debts": _dec2, "purchased_amount": _dec2,
            "is_discount_by_level": _int, "is_block": _int,
            "order_count": _int, "succeed_order_count": _int, "returned_order_count": _int,
            "count_referrals": _int, "total_amount_referred": _float,
            "last_order_at": _dt, "inserted_at": _dt, "updated_at": _dt,
        },
    },
    "addresses": {
        "table": "customer_addresses", "primary_key": "id",
        "fields": {
            "id": "id", "customer_id": "customer_id", "full_name": "full_name",
            "phone_number": "phone_number", "address": "address",
            "full_address": "full_address", "province_id": "province_id",
            "province_name": "province_name", "district_id": "district_id",
            "district_name": "district_name", "commune_id": "commune_id",
            "commune_name": "commune_name", "country_code": "country_code",
            "post_code": "post_code", "is_default": "is_default",
        },
        "transforms": {
            "phone_number": _str, "province_id": _str, "district_id": _str,
            "commune_id": _str, "country_code": _str, "post_code": _str, "is_default": _int,
        },
    },
    "order_items": {
        "table": "order_items", "primary_key": "id",
        "fields": {
            "id": "id", "order_id": "order_id", "product_id": "product_id",
            "variation_id": "variation_id", "variation_name": "variation_name",
            "quantity": "quantity", "retail_price": "retail_price",
            "discount_each_product": "discount_each_product",
            "is_discount_percent": "is_discount_percent", "same_price_discount": "same_price_discount",
            "total_discount": "total_discount", "tax_rate": "tax_rate", "weight": "weight",
            "note": "note", "note_product": "note_product",
            "is_bonus_product": "is_bonus_product", "is_composite": "is_composite",
            "is_wholesale": "is_wholesale", "one_time_product": "one_time_product",
            "return_quantity": "return_quantity", "returning_quantity": "returning_quantity",
            "returned_count": "returned_count", "exchange_count": "exchange_count",
            "added_to_cart_quantity": "added_to_cart_quantity",
            "composite_item_id": "composite_item_id", "item_id": "item_id",
            "product_name": "product_name",
        },
        "transforms": {
            "order_id": _int, "quantity": _int, "retail_price": _float,
            "discount_each_product": _dec2, "same_price_discount": _dec2,
            "total_discount": _float, "tax_rate": _dec2, "weight": _dec2,
            "is_discount_percent": _int, "is_bonus_product": _int, "is_composite": _int,
            "is_wholesale": _int, "one_time_product": _int,
            "return_quantity": _int, "returning_quantity": _int,
            "returned_count": _int, "exchange_count": _int, "added_to_cart_quantity": _int,
        },
    },
    "order_payments": {
        "table": "order_payments", "primary_key": "id",
        "fields": {
            "id": "id", "order_id": "order_id", "method": "method",
            "bank_name": "bank_name", "account_number": "account_number",
            "account_name": "account_name", "amount": "amount",
            "paid_at": "paid_at", "note": "note",
        },
        "transforms": {
            "order_id": _int, "amount": _dec2, "paid_at": _dt,
        },
    },
    "warehouses": {
        "table": "warehouses", "primary_key": "id",
        "fields": {
            "id": "id", "name": "name",
            "phone_number": "phone_number", "address": "address",
            "full_address": "full_address",
            "province_id": "province_id", "district_id": "district_id",
            "commune_id": "commune_id",
        },
        "transforms": {},
    },
    "categories": {
        "table": "categories", "primary_key": "id",
        "fields": {
            "id": "id", "shop_id": "shop_id",
            "text": "text",
            "is_admin_category": "is_admin_category",
            "nodes": "nodes", "third_party": "third_party",
        },
        "transforms": {
            "shop_id": _int, "is_admin_category": _int,
        },
    },
    "tags": {
        "table": "tags", "primary_key": "id",
        "fields": {
            "id": "id", "shop_id": "shop_id", "name": "name",
            "color": "color",
        },
        "transforms": {
            "shop_id": _int,
        },
    },
    "order_sources": {
        "table": "order_sources", "primary_key": "id",
        "fields": {
            "id": "id", "shop_id": "shop_id", "name": "name",
            "custom_id": "custom_id", "image": "image",
            "parent_id": "parent_id", "project_id": "project_id",
            "link_source_id": "link_source_id",
            "is_removed": "is_removed",
            "inserted_at": "inserted_at", "updated_at": "updated_at",
        },
        "transforms": {
            "shop_id": _int, "is_removed": _int,
            "inserted_at": _dt, "updated_at": _dt,
        },
    },
    "users": {
        "table": "users", "primary_key": "id",
        "fields": {
            "id": "id", "shop_id": "shop_id",
            "user_id": "user_id", "profile_id": "profile_id",
            "department_id": "department_id",
            "user.name": "name", "user.email": "email",
            "user.phone_number": "phone_number",
            "user.avatar_url": "avatar_url",
            "role": "role",
            "is_assigned": "is_assigned",
            "is_assigned_break_time": "is_assigned_break_time",
            "enable_api": "enable_api",
            "inserted_at": "inserted_at",
        },
        "transforms": {
            "shop_id": _int, "department_id": _int,
            "is_assigned": _int, "is_assigned_break_time": _int,
            "enable_api": _int,
            "inserted_at": _dt,
        },
    },
}

def transform_row(row, entity):
    fm = FIELD_MAPS.get(entity)
    if not fm:
        return row
    result = {}
    transforms = fm.get("transforms", {})
    for api_key, db_col in fm["fields"].items():
        val = _get_nested(row, api_key, row.get(api_key))
        if db_col in transforms:
            val = transforms[db_col](val)
        elif val is not None:
            if not isinstance(val, (int, float, bool, datetime)):
                val = _str(val)
        result[db_col] = val
    return result

def transform_batch(api_data, entity):
    return [transform_row(row, entity) for row in api_data]

def extract_from_order_detail(order_detail):
    """Extract nested data from order detail.
    Returns (customer, address, items, payments).
    NOTE: customer/address extracted from separate customer API, not from orders.
    """
    items = []
    for item in order_detail.get("items", []):
        if item.get("id"):
            item["order_id"] = order_detail.get("id")
            items.append(item)
    payments = []
    for pay in order_detail.get("payment_purchase_histories", []):
        if pay.get("id"):
            pay["order_id"] = order_detail.get("id")
            payments.append(pay)
    return {}, {}, items, payments


def extract_products_from_variations(variation_data):
    """Extract products from variations API response.
    Each variation has a nested 'product' object + 'product_id' field.
    product_id lives on the variation, not inside the nested product dict.
    Returns list of product dicts (deduped by product_id).
    """
    import config as _cfg
    seen = set()
    products = []
    for var in variation_data:
        prod = var.get("product")
        if not prod:
            continue
        pid = var.get("product_id")
        if pid and pid not in seen:
            seen.add(pid)
            row = {"product_id": pid, "shop_id": int(_cfg.SHOP_ID)}
            # Flatten nested product fields so field mapping "product.xxx" works
            for k, v in prod.items():
                row[f"product.{k}"] = v
            products.append(row)
    return products


def extract_addresses_from_customers(customer_data):
    """Extract addresses from customer API response.
    Each customer has shop_customer_addresses (nested array).
    Returns list of address dicts with customer_id set.
    """
    addresses = []
    for cust in customer_data:
        cust_id = cust.get("id")
        if not cust_id:
            continue
        for addr in cust.get("shop_customer_addresses", []):
            if addr.get("id"):
                addr["customer_id"] = cust_id
                addresses.append(addr)
    return addresses

