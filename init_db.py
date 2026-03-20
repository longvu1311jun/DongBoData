# init_db.py — Tạo database + tables phù hợp với POS API response
# Chạy: python init_db.py

import mariadb
import sys

DB_HOST = "100.70.133.122"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "123123123"
DB_NAME = "pos_sync"

conn = None
try:
    print(f"Connecting to MariaDB at {DB_HOST}:{DB_PORT}...")
    conn = mariadb.connect(
        host=DB_HOST, port=DB_PORT,
        user=DB_USER, password=DB_PASSWORD,
        connect_timeout=30
    )
    cur = conn.cursor()
    print("✓ Connected")

    # Tạo database
    print(f"Creating database '{DB_NAME}'...")
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cur.execute(f"USE {DB_NAME}")
    print(f"✓ Database '{DB_NAME}' ready")

    tables = {}

    # ── 1. shops ──────────────────────────────────────────────────
    tables["shops"] = """
    CREATE TABLE IF NOT EXISTS shops (
        id              VARCHAR(64)  PRIMARY KEY,
        name            VARCHAR(255) NOT NULL DEFAULT '',
        api_key         VARCHAR(64)  NOT NULL DEFAULT '',
        created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """

    # ── 2. products ───────────────────────────────────────────────
    # API: GET /products/{id} → data is direct object
    tables["products"] = """
    CREATE TABLE IF NOT EXISTS products (
        id                  VARCHAR(64)  PRIMARY KEY,
        shop_id             BIGINT       NOT NULL DEFAULT 0,
        display_id          VARCHAR(255) NOT NULL DEFAULT '',
        name                VARCHAR(255) NOT NULL DEFAULT '',
        image               TEXT,
        is_published        TINYINT      NOT NULL DEFAULT 0,
        note                TEXT,
        note_product        TEXT,
        measure_group_id    VARCHAR(64)  NOT NULL DEFAULT '',
        type                VARCHAR(64)  NOT NULL DEFAULT '',
        custom_id           VARCHAR(255) NOT NULL DEFAULT '',
        created_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_shop_id (shop_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """

    # ── 3. product_variations ─────────────────────────────────────
    # API: GET /products/variations → data[] has top-level fields + nested product
    tables["product_variations"] = """
    CREATE TABLE IF NOT EXISTS product_variations (
        id                          VARCHAR(64)   PRIMARY KEY,
        shop_id                     BIGINT        NOT NULL DEFAULT 0,
        product_id                  VARCHAR(64)   NOT NULL DEFAULT '',
        name                        VARCHAR(255)  NOT NULL DEFAULT '',
        display_id                  VARCHAR(255)  NOT NULL DEFAULT '',
        barcode                     VARCHAR(255)  NOT NULL DEFAULT '',
        retail_price                DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
        retail_price_original       DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
        retail_price_after_discount DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
        average_imported_price       DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
        avg_price                   DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
        price_at_counter            DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
        last_imported_price         DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
        total_purchase_price        DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
        wholesale_price             DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
        tax_rate                    DECIMAL(5,4)  NOT NULL DEFAULT 0.0000,
        weight                      DECIMAL(10,2)          DEFAULT NULL,
        is_hidden                   TINYINT       NOT NULL DEFAULT 0,
        is_locked                   TINYINT       NOT NULL DEFAULT 0,
        is_composite                TINYINT       NOT NULL DEFAULT 0,
        is_removed                  TINYINT       NOT NULL DEFAULT 0,
        is_sell_negative            TINYINT       NOT NULL DEFAULT 0,
        is_sell_negative_variation  TINYINT       NOT NULL DEFAULT 0,
        is_vat_inclusive            TINYINT       NOT NULL DEFAULT 0,
        is_upsale_product           TINYINT       NOT NULL DEFAULT 0,
        remain_quantity             INT           NOT NULL DEFAULT 0,
        inserted_at                 DATETIME(6)             DEFAULT NULL,
        created_at                  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at                  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_shop_id (shop_id),
        INDEX idx_product_id (product_id),
        CONSTRAINT fk_var_product FOREIGN KEY (product_id)
            REFERENCES products(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """

    # ── 4. variation_warehouse_stock ──────────────────────────────
    # Nested in product.json → variations[] → variations_warehouses[]
    tables["variation_warehouse_stock"] = """
    CREATE TABLE IF NOT EXISTS variation_warehouse_stock (
        variation_id             VARCHAR(64) NOT NULL DEFAULT '',
        warehouse_id            VARCHAR(64) NOT NULL DEFAULT '',
        remain_quantity         INT         NOT NULL DEFAULT 0,
        actual_remain_quantity  INT         NOT NULL DEFAULT 0,
        pending_quantity        INT         NOT NULL DEFAULT 0,
        waiting_quantity        INT         NOT NULL DEFAULT 0,
        returning_quantity      INT         NOT NULL DEFAULT 0,
        total_quantity          INT         NOT NULL DEFAULT 0,
        selling_avg             DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
        updated_at              DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (variation_id, warehouse_id),
        INDEX idx_warehouse (warehouse_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """

    # ── 5. warehouses ────────────────────────────────────────────
    # API: GET /shops/{shop_id}/warehouses → data[]
    tables["warehouses"] = """
    CREATE TABLE IF NOT EXISTS warehouses (
        id              VARCHAR(64)  PRIMARY KEY,
        shop_id         BIGINT       NOT NULL DEFAULT 0,
        name            VARCHAR(255) NOT NULL DEFAULT '',
        address         TEXT,
        is_default      TINYINT      NOT NULL DEFAULT 0,
        created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_shop_id (shop_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """

    # ── 6. customers ──────────────────────────────────────────────
    # API: GET /shops/{shop_id}/customers → data[]
    tables["customers"] = """
    CREATE TABLE IF NOT EXISTS customers (
        id                  VARCHAR(64)  PRIMARY KEY,
        shop_id             BIGINT       NOT NULL DEFAULT 0,
        display_id          VARCHAR(255) NOT NULL DEFAULT '',
        full_name           VARCHAR(255) NOT NULL DEFAULT '',
        first_name          VARCHAR(255) NOT NULL DEFAULT '',
        last_name           VARCHAR(255) NOT NULL DEFAULT '',
        phone_number        VARCHAR(32)  NOT NULL DEFAULT '',
        email               VARCHAR(255) NOT NULL DEFAULT '',
        gender              VARCHAR(16)  NOT NULL DEFAULT '',
        birthday            DATE,
        point               INT          NOT NULL DEFAULT 0,
        total_spent         DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
        total_orders        INT          NOT NULL DEFAULT 0,
        created_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_shop_id (shop_id),
        INDEX idx_phone (phone_number),
        INDEX idx_email (email)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """

    # ── 7. addresses ────────────────────────────────────────────
    # Nested in customer.json → addresses[]
    tables["addresses"] = """
    CREATE TABLE IF NOT EXISTS addresses (
        id              VARCHAR(64)  PRIMARY KEY,
        customer_id     VARCHAR(64)  NOT NULL DEFAULT '',
        full_name       VARCHAR(255) NOT NULL DEFAULT '',
        phone_number    VARCHAR(32)  NOT NULL DEFAULT '',
        address         TEXT,
        province_id     VARCHAR(64)  NOT NULL DEFAULT '',
        province_name   VARCHAR(255) NOT NULL DEFAULT '',
        district_id     VARCHAR(64)  NOT NULL DEFAULT '',
        district_name   VARCHAR(255) NOT NULL DEFAULT '',
        commune_id      VARCHAR(64)  NOT NULL DEFAULT '',
        commune_name    VARCHAR(255) NOT NULL DEFAULT '',
        is_default      TINYINT      NOT NULL DEFAULT 0,
        created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_customer_id (customer_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """

    # ── 8. orders ─────────────────────────────────────────────────
    # API: GET /shops/{shop_id}/orders (paginated) → data[]
    tables["orders"] = """
    CREATE TABLE IF NOT EXISTS orders (
        id                      VARCHAR(64)   PRIMARY KEY,
        shop_id                 BIGINT        NOT NULL DEFAULT 0,
        page_id                 VARCHAR(64)   NOT NULL DEFAULT '',
        order_code              VARCHAR(64)   NOT NULL DEFAULT '',
        conversation_id         VARCHAR(64)   NOT NULL DEFAULT '',
        post_id                 VARCHAR(64)   NOT NULL DEFAULT '',
        ad_id                   VARCHAR(64)   NOT NULL DEFAULT '',
        creator_id              VARCHAR(64)   NOT NULL DEFAULT '',
        assigning_seller_id     VARCHAR(64)   NOT NULL DEFAULT '',
        assigning_care_id       VARCHAR(64)   NOT NULL DEFAULT '',
        marketer_id             VARCHAR(64)   NOT NULL DEFAULT '',
        customer_id             VARCHAR(64)   NOT NULL DEFAULT '',
        warehouse_id             VARCHAR(64)   NOT NULL DEFAULT '',
        status                  VARCHAR(64)   NOT NULL DEFAULT '',
        sub_status              VARCHAR(64)   NOT NULL DEFAULT '',
        status_name             VARCHAR(255)  NOT NULL DEFAULT '',
        bill_full_name          VARCHAR(255)  NOT NULL DEFAULT '',
        bill_phone_number       VARCHAR(32)   NOT NULL DEFAULT '',
        bill_email              VARCHAR(255)  NOT NULL DEFAULT '',
        shipping_full_name      VARCHAR(255)  NOT NULL DEFAULT '',
        shipping_phone_number   VARCHAR(32)   NOT NULL DEFAULT '',
        shipping_address        TEXT,
        shipping_full_address   TEXT,
        shipping_province_id    VARCHAR(64)   NOT NULL DEFAULT '',
        shipping_province_name  VARCHAR(255)  NOT NULL DEFAULT '',
        shipping_district_id    VARCHAR(64)   NOT NULL DEFAULT '',
        shipping_district_name  VARCHAR(255)  NOT NULL DEFAULT '',
        shipping_commune_id     VARCHAR(64)   NOT NULL DEFAULT '',
        shipping_commune_name   VARCHAR(255)  NOT NULL DEFAULT '',
        shipping_country_code   VARCHAR(8)    NOT NULL DEFAULT '',
        total_price             DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
        total_discount          DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
        total_after_discount    DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
        shipping_cost           DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
        point_discount          DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
        coupon_discount         DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
        customer_shipping_free  TINYINT        NOT NULL DEFAULT 0,
        order_type              VARCHAR(32)    NOT NULL DEFAULT '',
        is_pos                  TINYINT        NOT NULL DEFAULT 0,
        is_video_order          TINYINT        NOT NULL DEFAULT 0,
        is_pay_later            TINYINT        NOT NULL DEFAULT 0,
        order_placed_at         DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
        created_at              DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at              DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_shop_id (shop_id),
        INDEX idx_order_code (order_code),
        INDEX idx_customer_id (customer_id),
        INDEX idx_status (status),
        INDEX idx_warehouse_id (warehouse_id),
        INDEX idx_creator_id (creator_id),
        INDEX idx_order_placed_at (order_placed_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """

    # ── 9. order_items ───────────────────────────────────────────
    # Nested in order detail → items[]
    tables["order_items"] = """
    CREATE TABLE IF NOT EXISTS order_items (
        id                  VARCHAR(64)   PRIMARY KEY,
        order_id            VARCHAR(64)   NOT NULL DEFAULT '',
        variation_id        VARCHAR(64)   NOT NULL DEFAULT '',
        product_id          VARCHAR(64)   NOT NULL DEFAULT '',
        product_name        VARCHAR(255)  NOT NULL DEFAULT '',
        variation_name      VARCHAR(255)  NOT NULL DEFAULT '',
        sku                 VARCHAR(255)  NOT NULL DEFAULT '',
        barcode             VARCHAR(255)  NOT NULL DEFAULT '',
        quantity            INT           NOT NULL DEFAULT 0,
        price               DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
        price_after_discount DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
        discount_amount     DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
        created_at          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_order_id (order_id),
        INDEX idx_variation_id (variation_id),
        INDEX idx_product_id (product_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """

    # ── 10. payments ──────────────────────────────────────────────
    # Nested in order detail → payment_purchase_histories[]
    tables["payments"] = """
    CREATE TABLE IF NOT EXISTS payments (
        id                  VARCHAR(64)   PRIMARY KEY,
        order_id            VARCHAR(64)   NOT NULL DEFAULT '',
        method              VARCHAR(64)   NOT NULL DEFAULT '',
        amount              DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
        status              VARCHAR(32)   NOT NULL DEFAULT '',
        transaction_no       VARCHAR(128)  NOT NULL DEFAULT '',
        payment_gateway     VARCHAR(64)   NOT NULL DEFAULT '',
        note                TEXT,
        created_at          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_order_id (order_id),
        INDEX idx_method (method),
        INDEX idx_status (status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """

    # ── 11. categories ───────────────────────────────────────────
    # API: GET /shops/{shop_id}/categories → data[]
    tables["categories"] = """
    CREATE TABLE IF NOT EXISTS categories (
        id              VARCHAR(64)  PRIMARY KEY,
        shop_id         BIGINT       NOT NULL DEFAULT 0,
        parent_id       VARCHAR(64)  NOT NULL DEFAULT '',
        name            VARCHAR(255) NOT NULL DEFAULT '',
        display_id      VARCHAR(64)  NOT NULL DEFAULT '',
        sort_order      INT          NOT NULL DEFAULT 0,
        is_active       TINYINT      NOT NULL DEFAULT 1,
        created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_shop_id (shop_id),
        INDEX idx_parent_id (parent_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """

    # ── 12. tags ─────────────────────────────────────────────────
    # API: GET /shops/{shop_id}/orders/tags → data[]
    tables["tags"] = """
    CREATE TABLE IF NOT EXISTS tags (
        id              VARCHAR(64)  PRIMARY KEY,
        shop_id         BIGINT       NOT NULL DEFAULT 0,
        name            VARCHAR(255) NOT NULL DEFAULT '',
        color           VARCHAR(32)  NOT NULL DEFAULT '',
        created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_shop_id (shop_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """

    # ── 13. order_sources ─────────────────────────────────────────
    # API: GET /shops/{shop_id}/order_source → data[]
    tables["order_sources"] = """
    CREATE TABLE IF NOT EXISTS order_sources (
        id              VARCHAR(64)  PRIMARY KEY,
        shop_id         BIGINT       NOT NULL DEFAULT 0,
        name            VARCHAR(255) NOT NULL DEFAULT '',
        created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_shop_id (shop_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """

    # ── 14. users ────────────────────────────────────────────────
    # API: GET /shops/{shop_id}/users → data[]
    tables["users"] = """
    CREATE TABLE IF NOT EXISTS users (
        id              VARCHAR(64)  PRIMARY KEY,
        shop_id         BIGINT       NOT NULL DEFAULT 0,
        display_id      VARCHAR(64)  NOT NULL DEFAULT '',
        full_name       VARCHAR(255) NOT NULL DEFAULT '',
        email           VARCHAR(255) NOT NULL DEFAULT '',
        phone_number    VARCHAR(32)  NOT NULL DEFAULT '',
        role            VARCHAR(32)  NOT NULL DEFAULT '',
        is_active       TINYINT      NOT NULL DEFAULT 1,
        created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_shop_id (shop_id),
        INDEX idx_email (email)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """

    # ── Tạo tables ──────────────────────────────────────────────
    for name, sql in tables.items():
        print(f"  Creating table '{name}'...")
        cur.execute(sql)
        print(f"    ✓ {name}")

    conn.commit()
    print(f"\n✅ Database '{DB_NAME}' — {len(tables)} tables created successfully!")

except mariadb.Error as e:
    print(f"❌ MariaDB Error: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}", file=sys.stderr)
    sys.exit(1)
finally:
    if conn:
        conn.close()

