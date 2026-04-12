-- Compliance rules
INSERT INTO rule (name, rule_type, threshold, target) VALUES
    ('Max single stock weight 10%',  'max_weight',          0.10,  NULL),
    ('No tobacco sector exposure',   'exclusion',           NULL,  'Tobacco'),
    ('Top-10 concentration < 60%',   'min_diversification', 0.60,  NULL),
    ('No single country over 50%',   'max_country_weight',  0.50,  NULL),
    ('Minimum 10 holdings required', 'min_holdings',        10.0,  NULL);

-- Sample portfolio
INSERT INTO portfolio (id, name) VALUES (1, 'Sample Portfolio');

INSERT INTO holding (portfolio_id, ticker, isin, sector, country, weight) VALUES
    (1, 'AAPL',  'US0378331005', 'Technology',             'USA',         0.142),
    (1, 'MSFT',  'US5949181045', 'Technology',             'USA',         0.098),
    (1, 'NESN',  'CH0012221716', 'Consumer Staples',       'Switzerland', 0.075),
    (1, 'NOVN',  'CH0012221716', 'Healthcare',             'Switzerland', 0.063),
    (1, 'BALN',  'CH0012221716', 'Tobacco',                'Switzerland', 0.031),
    (1, 'ROG',   'CH0012221716', 'Healthcare',             'Switzerland', 0.058),
    (1, 'GOOGL', 'US02079K3059', 'Technology',             'USA',         0.089),
    (1, 'AMZN',  'US0231351067', 'Consumer Discretionary', 'USA',         0.072),
    (1, 'JPM',   'US46625H1005', 'Financials',             'USA',         0.045),
    (1, 'BLK',   'US09248X1081', 'Financials',             'USA',         0.038),
    (1, 'SHEL',  'GB00BP6MXD84', 'Energy',                 'UK',          0.041),
    (1, 'ASML',  'NL0010273215', 'Technology',             'Netherlands', 0.055),
    (1, 'LVMH',  'FR0000121014', 'Consumer Discretionary', 'France',      0.049),
    (1, 'MC',    'FR0000121014', 'Consumer Discretionary', 'France',      0.044),
    (1, 'SAN',   'ES0113900J37', 'Financials',             'Spain',       0.036),
    (1, 'UBSG',  'CH0244767585', 'Financials',             'Switzerland', 0.065);
