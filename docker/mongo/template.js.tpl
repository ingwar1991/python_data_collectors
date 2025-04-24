db = db.getSiblingDB("$MONGO_DB_NAME");

db.createUser({
    user: "$MONGO_USER",
    pwd: "$MONGO_USER_PASS",
    roles: [{ role: "readWrite", db: "$MONGO_DB_NAME" }]
});

db.createCollection('hostsDiscovered', {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["unique_id", "source", "ip", "mac", "os", "os_version", "name", "first_seen", "last_seen"],
            properties: {
                unique_id: { bsonType: "string" },
                source: { bsonType: "string" },
                ip: { bsonType: "string" },
                mac: { bsonType: "string" },
                os: { bsonType: "string" },
                os_version: { bsonType: "string" },
                name: { bsonType: "string" },
                first_seen: {bsonType: "date"},
                last_seen: {bsonType: "date"}
            }
        }
    }
});
