import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 100 }, // Ramp-up to 100 users in 30 seconds
  ],
};

export default function () {
    // Define your payload based on the ProductRequest model
    let payload = JSON.stringify({
      name: "Sample Product",
      description: "A high-quality sample product for testing.",
      price: 49.99,
      category: "Electronics",
      stock: 100,
      availability: true,
      image: "https://example.com/product-image.jpg",
      ratings: 4.5,
      discount: 10.0,
      manufacturer: "Sample Manufacturer",
      brand: "Sample Brand",
      tags: ["electronics", "sample", "test"]
    });
  
    // Set headers for the request
    let headers = { 'Content-Type': 'application/json' };
  
    // Send POST request to the /product endpoint
    let res = http.post('http://localhost:8000/product', payload, { headers });
  
    // Validate the response status code is 200
    check(res, {
      'is status 200': (r) => r.status === 200,
    });
  }