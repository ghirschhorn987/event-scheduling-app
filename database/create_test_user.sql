-- Script to create a test user 'test1@skeddle.club' with password 'test1'
-- Run this in the Supabase SQL Editor

-- Ensure pgcrypto is available for password hashing
create extension if not exists pgcrypto;

DO $$
DECLARE
  new_user_id uuid := gen_random_uuid();
  user_email text := 'test1@skeddle.club';
  user_password text := 'test1';
  user_name text := 'Test User 1';
BEGIN
  -- 1. Insert into auth.users (if not exists)
  IF NOT EXISTS (SELECT 1 FROM auth.users WHERE email = user_email) THEN
    INSERT INTO auth.users (
      id,
      email,
      encrypted_password,
      email_confirmed_at,
      raw_app_meta_data,
      raw_user_meta_data,
      created_at,
      updated_at,
      role,
      aud,
      confirmation_token
    )
    VALUES (
      new_user_id,
      user_email,
      crypt(user_password, gen_salt('bf')), -- Hash the password
      now(), -- Auto-confirm email
      '{"provider":"email","providers":["email"]}',
      jsonb_build_object('full_name', user_name),
      now(),
      now(),
      'authenticated',
      'authenticated',
      ''
    );
    
    RAISE NOTICE 'Created auth user %', user_email;
  ELSE
    -- If user exists, get their ID
    SELECT id INTO new_user_id FROM auth.users WHERE email = user_email;
    RAISE NOTICE 'Auth user % already exists, using ID %', user_email, new_user_id;
  END IF;

  -- 2. Insert into public.profiles (if not exists)
  INSERT INTO public.profiles (id, email, name)
  VALUES (new_user_id, user_email, user_name)
  ON CONFLICT (id) DO NOTHING;
  
  RAISE NOTICE 'Ensured profile for %', user_email;
END $$;
