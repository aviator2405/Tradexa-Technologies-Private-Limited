import threading
import csv
from django.db import transaction, connection, DatabaseError
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from webapp.models import Users, Products, Orders

class CSVUploadAPIView(APIView):
    parser_classes = [MultiPartParser]
    lock = threading.Lock()  # Shared lock for critical sections

    def post(self, request):
        print("Received request to upload CSV files.")
        files = {
            "users": request.FILES.get("users"),
            "products": request.FILES.get("products"),
            "orders": request.FILES.get("orders")
        }

        if not all(files.values()):
            print("Error: Missing one or more required CSV files.")
            return JsonResponse({"error": "Please upload all three CSV files."}, status=400)

        results = []

        def validate_users(data):
            print("Validating user data...")
            errors = []
            valid_records = []
            for row in data:
                if not row.get("id") or not row.get("name") or not row.get("email"):
                    errors.append(f"Invalid user data: {row}")
                else:
                    valid_records.append(row)
            print(f"User validation complete. Valid records: {len(valid_records)}, Errors: {len(errors)}")
            return errors, valid_records

        def validate_products(data):
            print("Validating product data...")
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
            print(f"Product validation complete. Valid records: {len(valid_records)}, Errors: {len(errors)}")
            return errors, valid_records

        def validate_orders(data):
            print("Validating order data...")
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
            print(f"Order validation complete. Valid records: {len(valid_records)}, Errors: {len(errors)}")
            return errors, valid_records

        def process_users():
            print("Processing user data...")
            with files["users"].open() as f:
                content = f.read().decode("utf-8-sig").splitlines()
                reader = csv.DictReader(content)
                data = list(reader)
                errors, valid_data = validate_users(data)
                records = []
                with CSVUploadAPIView.lock:
                    print("Lock acquired for user processing.")
                    for row in valid_data:
                        if Users.objects.filter(id=row["id"]).exists():
                            errors.append(f"User with id {row['id']} already exists. Skipping.")
                            continue
                        records.append(Users(id=row["id"], name=row["name"], emails=row["email"]))
                    print("Releasing lock for user processing.")
                if records:
                    Users.objects.bulk_create(records)
                print(f"User processing complete. Records created: {len(records)}, Errors: {len(errors)}")
                results.append({"users_errors": errors})

        def process_products():
            print("Processing product data...")
            with files["products"].open() as f:
                content = f.read().decode("utf-8-sig").splitlines()
                reader = csv.DictReader(content)
                data = list(reader)
                errors, valid_data = validate_products(data)
                records = []
                with CSVUploadAPIView.lock:
                    print("Lock acquired for product processing.")
                    for row in valid_data:
                        if Products.objects.filter(id=row["id"]).exists():
                            errors.append(f"Product with id {row['id']} already exists. Skipping.")
                            continue
                        records.append(Products(id=row["id"], name=row["name"], price=float(row["price"])))
                    print("Releasing lock for product processing.")
                if records:
                    Products.objects.bulk_create(records)
                print(f"Product processing complete. Records created: {len(records)}, Errors: {len(errors)}")
                results.append({"products_errors": errors})

        def process_orders():
            print("Processing order data...")
            try:
                with files["orders"].open() as f:
                    content = f.read().decode("utf-8-sig").splitlines()
                    reader = csv.DictReader(content)
                    data = list(reader)
                    errors, valid_data = validate_orders(data)
                    records = []
                    with transaction.atomic():
                        with CSVUploadAPIView.lock:
                            print("Lock acquired for order processing.")
                            for row in valid_data:
                                if Orders.objects.filter(id=row["id"]).exists():
                                    errors.append(f"Order with id {row['id']} already exists. Skipping.")
                                    continue
                                try:
                                    user = Users.objects.get(id=row["user_id"])
                                    product = Products.objects.select_for_update().get(id=row["product_id"])
                                    records.append(Orders(id=row["id"], user_id=user, product_id=product, quantity=int(row["quantity"])))
                                except Users.DoesNotExist:
                                    errors.append(f"User with id {row['user_id']} does not exist.")
                                except Products.DoesNotExist:
                                    errors.append(f"Product with id {row['product_id']} does not exist.")
                            print("Releasing lock for order processing.")
                        if records:
                            Orders.objects.bulk_create(records)
                    print(f"Order processing complete. Records created: {len(records)}, Errors: {len(errors)}")
                    results.append({"orders_errors": errors})
            except DatabaseError as e:
                print(f"Transaction blocked or failed: {str(e)}")
                results.append({"error": f"Transaction blocked or failed: {str(e)}"})
            finally:
                connection.close()
                print("Database connection closed.")

        # Process users and products concurrently
        print("Starting user and product processing threads.")
        user_thread = threading.Thread(target=process_users)
        product_thread = threading.Thread(target=process_products)

        user_thread.start()
        product_thread.start()

        user_thread.join()
        product_thread.join()
        print("User and product processing threads completed.")

        # Process orders after users and products
        print("Starting order processing.")
        process_orders()

        print("All processing completed. Sending response.")
        return JsonResponse({"message": "Process completed.", "details": results}, status=200)
