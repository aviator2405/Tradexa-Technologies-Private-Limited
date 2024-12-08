import threading
import csv
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from webapp.models import Users, Products, Orders

class CSVUploadAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        files = {
            "users": request.FILES.get("users"),
            "products": request.FILES.get("products"),
            "orders": request.FILES.get("orders")
        }

        if not all(files.values()):
            return JsonResponse({"error": "Please upload all three CSV files."}, status=400)

        results = []

        def validate_users(data):
            print("Raw Users Data:", data)  # Debugging line
            errors = []
            valid_records = []
            for row in data:
                if not row.get("id") or not row.get("name") or not row.get("email"):
                    errors.append(f"Invalid user data: {row}")
                else:
                    valid_records.append(row)
            return errors, valid_records

        def validate_products(data):
            print("Raw Products Data:", data)  # Debugging line
            errors = []
            valid_records = []
            for row in data:
                if not row.get("id") or not row.get("name") or not row.get("price"):
                    errors.append(f"Invalid product data: {row}")
                else:
                    try:
                        price = float(row["price"])
                        if price <= 0:
                            errors.append(f"Product with id {row['id']} has invalid price: {price}.")
                        else:
                            valid_records.append(row)
                    except ValueError:
                        errors.append(f"Invalid price value: {row}")
            return errors, valid_records

        def validate_orders(data):
            print("Raw Orders Data:", data)  # Debugging line
            errors = []
            valid_records = []
            for row in data:
                if not row.get("id") or not row.get("user_id") or not row.get("product_id") or not row.get("quantity"):
                    errors.append(f"Invalid order data: {row}")
                else:
                    try:
                        quantity = int(row["quantity"])
                        if quantity <= 0:
                            errors.append(f"Order with id {row['id']} has invalid quantity: {quantity}.")
                        else:
                            valid_records.append(row)
                    except ValueError:
                        errors.append(f"Invalid quantity value: {row}")
            return errors, valid_records

        def process_users():
            with files["users"].open() as f:
                # Decode and remove BOM if present
                content = f.read().decode("utf-8-sig").splitlines()
                reader = csv.DictReader(content)
                data = list(reader)
                print("Parsed Users Data:", data)  # Debugging line
                errors, valid_data = validate_users(data)
                print("Validation Errors:", errors)  # Debugging line
                print("Validated Users Data:", valid_data)  # Debugging line
                records = []
                for row in valid_data:
                    if Users.objects.filter(id=row["id"]).exists():
                        errors.append(f"User with id {row['id']} already exists. Skipping.")
                        continue
                    records.append(Users(id=row["id"], name=row["name"], emails=row["email"]))
                if records:
                    Users.objects.bulk_create(records)
                    print(f"{len(records)} users inserted successfully.")
                else:
                    print("No valid user records to insert.")
            results.append({"users_errors": errors})

        def process_products():
            with files["products"].open() as f:
                # Decode and remove BOM if present
                content = f.read().decode("utf-8-sig").splitlines()
                reader = csv.DictReader(content)
                data = list(reader)
                print("Parsed Products Data:", data)  # Debugging line
                errors, valid_data = validate_products(data)
                print("Validation Errors:", errors)  # Debugging line
                print("Validated Products Data:", valid_data)  # Debugging line
                records = []
                for row in valid_data:
                    if Products.objects.filter(id=row["id"]).exists():
                        errors.append(f"Product with id {row['id']} already exists. Skipping.")
                        continue
                    records.append(Products(id=row["id"], name=row["name"], price=float(row["price"])))
                if records:
                    Products.objects.bulk_create(records)
                    print(f"{len(records)} products inserted successfully.")
                else:
                    print("No valid product records to insert.")
            results.append({"products_errors": errors})

        def process_orders():
            with files["orders"].open() as f:
                # Decode and remove BOM if present
                content = f.read().decode("utf-8-sig").splitlines()
                reader = csv.DictReader(content)
                data = list(reader)
                print("Parsed Orders Data:", data)  # Debugging line
                errors, valid_data = validate_orders(data)
                print("Validation Errors:", errors)  # Debugging line
                print("Validated Orders Data:", valid_data)  # Debugging line
                records = []
                for row in valid_data:
                    if Orders.objects.filter(id=row["id"]).exists():
                        errors.append(f"Order with id {row['id']} already exists. Skipping.")
                        continue
                    try:
                        user = Users.objects.get(id=row["user_id"])
                        product = Products.objects.get(id=row["product_id"])
                        records.append(Orders(id=row["id"], user_id=user, product_id=product, quantity=int(row["quantity"])))
                    except Users.DoesNotExist:
                        errors.append(f"User with id {row['user_id']} does not exist.")
                    except Products.DoesNotExist:
                        errors.append(f"Product with id {row['product_id']} does not exist.")
                if records:
                    Orders.objects.bulk_create(records)
                    print(f"{len(records)} orders inserted successfully.")
                else:
                    print("No valid order records to insert.")
            results.append({"orders_errors": errors})

        # Process users and products concurrently
        user_thread = threading.Thread(target=process_users)
        product_thread = threading.Thread(target=process_products)

        user_thread.start()
        product_thread.start()

        user_thread.join()
        product_thread.join()

        # Process orders after users and products
        process_orders()

        return JsonResponse({"message": "Process completed.", "details": results}, status=200)
