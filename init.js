db.createUser({
    user: "ricardo",
    pwd: "ricardo",
    roles: [
        {
            role: "readWrite",
            db: "my-mongo-db"
        }
    ]
});