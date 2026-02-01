UPDATE events 
SET 
  roster_sign_up_open = NOW() - INTERVAL '1 day',
  reserve_sign_up_open = NOW() + INTERVAL '1 day'
WHERE name = 'Weekly Basketball';
