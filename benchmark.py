import timeit
from faker import Faker
from pydantic import BaseModel, ValidationError
from typing import List
from dataclasses import dataclass
import random

# Initialize Faker instance
fake = Faker()

# Define the Pydantic Product model
class ProductSchema(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: str
    
@dataclass
class Product:
    id: int
    name: str
    description: str
    price: float
    category: str

def generate_products_dataclass(n: int = 100_000) -> List[Product]:
    """
    Generates a list of Product instances with fake data.

    Args:
        n (int): Number of products to generate.

    Returns:
        List[Product]: A list of validated Product instances.
    """
    categories = ['Electronics', 'Clothing', 'Books', 'Toys', 'Furniture']
    products = []
    
    for i in range(n):
        product_id = i + 1
        name = fake.word()
        description = fake.text(max_nb_chars=200)  # Limit description length
        price = round(random.uniform(5.0, 500.0), 2)
        category = random.choice(categories)
        
        if isinstance(product_id, int) and isinstance(name, str) and isinstance(description, str) \
                and isinstance(price, float) and isinstance(category, str):
            product = Product(
                id=product_id,
                name=name,
                description=description,
                price=price,
                category=category
            )
            products.append(product)
        else:
            print(f"Validation error for product id {product_id}")
        
    return products

def generate_products(n=100_000):
    """
    Generates a list of Product instances with fake data.

    Args:
        n (int): Number of products to generate.

    Returns:
        List[Product]: A list of validated Product instances.
    """
    categories = ['Electronics', 'Clothing', 'Books', 'Toys', 'Furniture']
    products = []
    
    for i in range(n):
        try:
            product = ProductSchema(
                id=i + 1,
                name=fake.word(),
                description=fake.text(max_nb_chars=200),  # Limit description length
                price=round(random.uniform(5.0, 500.0), 2),
                category=random.choice(categories)
            )
            products.append(product)
        except ValidationError as e:
            # Handle validation errors if any
            print(f"Validation error for product id {i + 1}: {e}")
    
    return products

if __name__ == "__main__":
    # Define the number of products to generate
    NUM_PRODUCTS = 100000

    # Benchmark the product generation and validation
    time_taken = timeit.timeit(lambda: generate_products_dataclass(NUM_PRODUCTS), number=10)
    print(f"Dataclass: Time taken to generate and validate {NUM_PRODUCTS} products: {time_taken:.4f} seconds")
    
    time_taken_pydantic = timeit.timeit(lambda: generate_products_dataclass(NUM_PRODUCTS), number=10)
    print(f"Pydantic: Time taken to generate and validate {NUM_PRODUCTS} products: {time_taken_pydantic:.4f} seconds")
    
    