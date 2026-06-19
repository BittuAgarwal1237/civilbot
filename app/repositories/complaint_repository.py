from app.database.mongodb import complaints_collection

def save_complaint(data: dict):

    result = complaints_collection.insert_one(data)

    return str(result.inserted_id)