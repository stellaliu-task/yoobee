-- 创建数据库表结构
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  name VARCHAR(255),
  role ENUM('admin', 'customer') NOT NULL DEFAULT 'customer',
  blocked BOOLEAN NOT NULL DEFAULT false
);

CREATE TABLE IF NOT EXISTS vehicles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  make VARCHAR(100) NOT NULL,
  model VARCHAR(100) NOT NULL,
  year INT NOT NULL,
  mileage INT NOT NULL,
  available_now BOOLEAN NOT NULL DEFAULT true,
  minimum_rent_period INT NOT NULL DEFAULT 1,
  maximum_rent_period INT NOT NULL DEFAULT 30,
  seats INT NOT NULL DEFAULT 5,
  price_per_day DECIMAL(10, 2) NOT NULL,
  image_url VARCHAR(512)
);

CREATE TABLE IF NOT EXISTS extras (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  fee DECIMAL(10, 2) NOT NULL,
  active BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE IF NOT EXISTS bookings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  vehicle_id INT NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  status ENUM('pending', 'approved', 'rejected', 'cancelled') NOT NULL DEFAULT 'pending',
  total_fee DECIMAL(10, 2) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
);

CREATE TABLE IF NOT EXISTS booking_extras (
  id INT AUTO_INCREMENT PRIMARY KEY,
  booking_id INT NOT NULL,
  extra_id INT NOT NULL,
  fee DECIMAL(10, 2) NOT NULL,
  FOREIGN KEY (booking_id) REFERENCES bookings(id),
  FOREIGN KEY (extra_id) REFERENCES extras(id)
);

-- 使用存储过程来处理数据插入
DELIMITER //
CREATE PROCEDURE init_sample_data()
BEGIN
    -- 检查users表是否存在
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'users') THEN
        -- 检查是否已有数据
        IF (SELECT COUNT(*) FROM users) = 0 THEN
            -- 插入用户账户
            -- 密码为: admin123!
            INSERT INTO users (email, hashed_password, name, role, blocked) VALUES
            ('admin@rentflex.com', '$2b$12$QiXF5e673kbWZ4WxOx.7XeVqf9/svND/AZqqR9J.M82iYkUVORMqS', 'System Admin', 'admin', false),
            ('customer@example.com', '$2b$12$QiXF5e673kbWZ4WxOx.7XeVqf9/svND/AZqqR9J.M82iYkUVORMqS', 'Test Customer', 'customer', false);
        END IF;
    END IF;

    -- 检查extras表是否存在
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'extras') THEN
        -- 检查是否已有数据
        IF (SELECT COUNT(*) FROM extras) = 0 THEN
            -- 插入额外服务数据
            INSERT INTO extras (name, description, fee, active) VALUES
            ('GPS Navigation', 'Full GPS navigation system', 50.00, true),
            ('Child Seat', 'Safety seat suitable for children aged 3-12', 30.00, true),
            ('Additional Driver', 'Add one more authorized driver', 100.00, true),
            ('Full Insurance', 'Comprehensive vehicle insurance coverage', 200.00, true);
        END IF;
    END IF;

    -- 检查vehicles表是否存在
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'vehicles') THEN
        -- 检查是否已有数据
        IF (SELECT COUNT(*) FROM vehicles) = 0 THEN
            -- 插入示例车辆
            INSERT INTO vehicles (make, model, year, mileage, available_now, minimum_rent_period, maximum_rent_period, seats, price_per_day, image_url) VALUES
            ('Toyota', 'Camry', 2023, 5000, true, 1, 30, 5, 300.00, 'https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?w=500'),
            ('Honda', 'Accord', 2022, 8000, true, 1, 30, 5, 280.00, 'https://images.unsplash.com/photo-1617469767053-d3b523a0b982?w=500'),
            ('Tesla', 'Model 3', 2023, 3000, true, 2, 20, 5, 500.00, 'https://images.unsplash.com/photo-1619722087489-f0b1a6d2e62f?w=500'),
            ('Mercedes', 'E-Class', 2022, 6000, true, 3, 30, 5, 600.00, 'https://images.unsplash.com/photo-1617531653332-bd46c24f2068?w=500'),
            ('BMW', '5 Series', 2023, 4500, true, 2, 25, 5, 550.00, 'https://images.unsplash.com/photo-1556189250-72ba954cfc2b?w=500'),
            ('Audi', 'A6', 2022, 7000, true, 2, 30, 5, 520.00, 'https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?w=500'),
            ('Volkswagen', 'Passat', 2023, 5500, true, 1, 30, 5, 260.00, 'https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?w=500');
        END IF;
    END IF;

    -- 检查bookings和booking_extras表是否存在，以及是否已有数据
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'bookings') AND
       EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'booking_extras') THEN
        -- 检查bookings表是否为空
        IF (SELECT COUNT(*) FROM bookings) = 0 THEN
            -- 创建示例预订（只有在users和vehicles已经有数据的情况下）
            IF (SELECT COUNT(*) FROM users) > 0 AND (SELECT COUNT(*) FROM vehicles) > 0 THEN
                -- 插入示例预订，使用查询到的用户和车辆ID
                SET @customer_id = (SELECT id FROM users WHERE role = 'customer' LIMIT 1);
                SET @vehicle_id1 = (SELECT id FROM vehicles WHERE make = 'Toyota' LIMIT 1);
                SET @vehicle_id2 = (SELECT id FROM vehicles WHERE make = 'Tesla' LIMIT 1);
                
                IF @customer_id IS NOT NULL AND @vehicle_id1 IS NOT NULL AND @vehicle_id2 IS NOT NULL THEN
                    INSERT INTO bookings (user_id, vehicle_id, start_date, end_date, status, total_fee) VALUES
                    (@customer_id, @vehicle_id1, '2023-06-10', '2023-06-15', 'approved', 1500.00),
                    (@customer_id, @vehicle_id2, '2023-07-05', '2023-07-10', 'pending', 2500.00);
                    
                    -- 为预订添加额外服务
                    IF (SELECT COUNT(*) FROM extras) > 0 THEN
                        SET @booking_id1 = (SELECT id FROM bookings ORDER BY id LIMIT 1);
                        SET @booking_id2 = (SELECT id FROM bookings ORDER BY id DESC LIMIT 1);
                        SET @extra_id1 = (SELECT id FROM extras WHERE name = 'GPS Navigation' LIMIT 1);
                        SET @extra_id2 = (SELECT id FROM extras WHERE name = 'Child Seat' LIMIT 1);
                        SET @extra_id4 = (SELECT id FROM extras WHERE name = 'Full Insurance' LIMIT 1);
                        
                        IF @booking_id1 IS NOT NULL AND @booking_id2 IS NOT NULL AND 
                           @extra_id1 IS NOT NULL AND @extra_id2 IS NOT NULL AND @extra_id4 IS NOT NULL THEN
                            INSERT INTO booking_extras (booking_id, extra_id, fee) VALUES
                            (@booking_id1, @extra_id1, 50.00),
                            (@booking_id1, @extra_id2, 30.00),
                            (@booking_id2, @extra_id4, 200.00);
                        END IF;
                    END IF;
                END IF;
            END IF;
        END IF;
    END IF;
END//
DELIMITER ;

-- 调用存储过程
CALL init_sample_data();

-- 清理存储过程
DROP PROCEDURE IF EXISTS init_sample_data; 