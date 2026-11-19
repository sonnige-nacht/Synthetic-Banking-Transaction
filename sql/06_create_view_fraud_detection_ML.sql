CREATE VIEW dw.vw_fraud_ml AS
SELECT
    t.transaction_id,
    t.timestamp,
    t.customer_id,
    t.card_id,
    t.device_id,
    t.ip_address,
    t.merchant_id,
    t.merchant_category,
    t.merchant_country,
    t.merchant_city,
    t.merchant_latitude,
    t.merchant_longitude,
    t.transaction_type,
    t.amount,
    t.currency,
    t.transaction_time,
    t.transaction_hour,
    t.transaction_minute,
    t.day_of_week,
    t.day_of_month,
    t.transaction_month,
    t.transaction_year,
    t.is_night,

    f.is_fraud,
    f.fraud_type

FROM dw.transactions AS t
LEFT JOIN dw.fraud_status AS f
    ON t.transaction_id = f.transaction_id;