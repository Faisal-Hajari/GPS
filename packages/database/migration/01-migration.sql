-- Source Tables 
CREATE TABLE cameras (
    uid         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(255) NOT NULL,
    location    GEOGRAPHY(POINT, 4326) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE images (
    uid         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    camera_uid  UUID NOT NULL REFERENCES cameras(uid) ON DELETE CASCADE,
    url         TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);


-- AI Model Events 
CREATE TABLE detected_objects (
    uid             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    image_uid       UUID NOT NULL REFERENCES images(uid) ON DELETE CASCADE,
    object_type     VARCHAR(50) NOT NULL,  -- 'car', 'person', 'house', etc.
    bounding_box    FLOAT[4] NOT NULL,
    confidence      FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    embedding       VECTOR(512),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE detected_cars (
    uid             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    object_uid      UUID NOT NULL REFERENCES detected_objects(uid) ON DELETE CASCADE,
    color           VARCHAR(50),
    make            VARCHAR(50),
    model           VARCHAR(50),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE car_plates (
    uid             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    car_uid         UUID NOT NULL REFERENCES detected_cars(uid) ON DELETE CASCADE,
    plate_number    VARCHAR(30) NOT NULL,
    bounding_box    FLOAT[4] NOT NULL,
    confidence      FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE detected_persons (
    uid             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    object_uid      UUID NOT NULL REFERENCES detected_objects(uid) ON DELETE CASCADE,
    age_estimate    INT,
    gender_estimate VARCHAR(20),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);