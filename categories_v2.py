import os
import pandas as pd
import numpy as np
import json 
from neo4j_manager import Neo4jManager
from score_calculator import ScoreCalculator
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

businesses = [
    {"category": "Agriculture", "name": "Organic Farming"},
    {"category": "Agriculture", "name": "Dairy Farm"},
    {"category": "Agriculture", "name": "Greenhouse"},
    {"category": "Agriculture", "name": "Fish Farming"},
    {"category": "Agriculture", "name": "Urban Farming"},
    {"category": "Agriculture", "name": "Beekeeping"},
    {"category": "Agriculture", "name": "Livestock Farming (Cattle, Sheep, Poultry)"},
    {"category": "Agriculture", "name": "Agricultural Machinery & Equipment"},
    {"category": "Agriculture", "name": "Agro-processing (e.g., Food Production)"},
    {"category": "Agriculture", "name": "Crop Farming (e.g., Cereals, Vegetables, Fruits)"},
    {"category": "Agriculture", "name": "Horticulture"},
    {"category": "Agriculture", "name": "Landscaping Services"},
    {"category": "Agriculture", "name": "Tree Farming & Forestry"},
    
    {"category": "Arts & Crafts", "name": "Photography"},
    {"category": "Arts & Crafts", "name": "Painting Services"},
    {"category": "Arts & Crafts", "name": "Handmade Jewelry"},
    {"category": "Arts & Crafts", "name": "Ceramics Studio"},
    {"category": "Arts & Crafts", "name": "Graphic Design"},
    {"category": "Arts & Crafts", "name": "Sculpture"},
    {"category": "Arts & Crafts", "name": "Textile & Fashion Design"},
    {"category": "Arts & Crafts", "name": "Pottery"},
    {"category": "Arts & Crafts", "name": "Woodworking"},
    {"category": "Arts & Crafts", "name": "Printing & Embroidery"},
    {"category": "Arts & Crafts", "name": "Craft Supplies Store"},
    
    {"category": "Automotive", "name": "Car Dealership"},
    {"category": "Automotive", "name": "Auto Repair Shop"},
    {"category": "Automotive", "name": "Car Wash"},
    {"category": "Automotive", "name": "Tire Shop"},
    {"category": "Automotive", "name": "Auto Body Shop"},
    {"category": "Automotive", "name": "Motorcycle Dealership"},
    {"category": "Automotive", "name": "Electric Vehicle Charging Stations"},
    {"category": "Automotive", "name": "RV Rental"},
    {"category": "Automotive", "name": "Fleet Management"},
    {"category": "Automotive", "name": "Vehicle Leasing"},
    {"category": "Automotive", "name": "Car Rental Services"},
    {"category": "Automotive", "name": "Auto Parts & Accessories Store"},
    
    {"category": "Construction", "name": "General Contractor"},
    {"category": "Construction", "name": "Home Renovation"},
    {"category": "Construction", "name": "Landscaping"},
    {"category": "Construction", "name": "Roofing Services"},
    {"category": "Construction", "name": "Solar Panel Installation"},
    {"category": "Construction", "name": "Plumbing"},
    {"category": "Construction", "name": "Electrical Services"},
    {"category": "Construction", "name": "HVAC Services"},
    {"category": "Construction", "name": "Interior Design"},
    {"category": "Construction", "name": "Civil Engineering & Consulting"},
    {"category": "Construction", "name": "Architecture & Urban Planning"},
    {"category": "Construction", "name": "Concrete Services"},
    {"category": "Construction", "name": "Demolition Services"},
    {"category": "Construction", "name": "Building Materials Supply"},
    
    {"category": "E-commerce", "name": "Online Clothing Store"},
    {"category": "E-commerce", "name": "Dropshipping"},
    {"category": "E-commerce", "name": "Handmade Goods"},
    {"category": "E-commerce", "name": "Subscription Box Service"},
    {"category": "E-commerce", "name": "Marketplace Platform"},
    {"category": "E-commerce", "name": "Online Grocery Store"},
    {"category": "E-commerce", "name": "Digital Products (E-books, Software)"},
    {"category": "E-commerce", "name": "Online Electronics Store"},
    {"category": "E-commerce", "name": "Custom Products (Printing, T-shirt Design)"},
    {"category": "E-commerce", "name": "Online Art Gallery"},
    {"category": "E-commerce", "name": "Online Beauty Products Store"},
    {"category": "E-commerce", "name": "Online Health & Wellness Products Store"},
    {"category": "Education", "name": "Tutoring Center"},
    {"category": "Education", "name": "Language School"},
    {"category": "Education", "name": "Childcare Center"},
    {"category": "Education", "name": "Driving School"},
    {"category": "Education", "name": "Online Courses"},
    {"category": "Education", "name": "Art School"},
    {"category": "Education", "name": "STEM Education Center"},
    {"category": "Education", "name": "Exam Preparation Services"},
    {"category": "Education", "name": "Vocational Training"},
    {"category": "Education", "name": "Music School"},
    {"category": "Education", "name": "Special Education Services"},
    {"category": "Education", "name": "Test Centers"},
    {"category": "Education", "name": "Corporate Training & Development"},
    {"category": "Entertainment", "name": "Movie Theater"},
    {"category": "Entertainment", "name": "Arcade"},
    {"category": "Entertainment", "name": "Event Planning"},
    {"category": "Entertainment", "name": "Live Music Venue"},
    {"category": "Entertainment", "name": "Amusement Park"},
    {"category": "Entertainment", "name": "Escape Room"},
    {"category": "Entertainment", "name": "Virtual Reality Arcade"},
    {"category": "Entertainment", "name": "Comedy Club"},
    {"category": "Entertainment", "name": "Video Game Development"},
    {"category": "Entertainment", "name": "Performing Arts School"},
    {"category": "Entertainment", "name": "Concert Production"},
    {"category": "Entertainment", "name": "Party Supplies Rentals"},
    {"category": "Entertainment", "name": "Wedding Planning"},
    {"category": "Finance", "name": "Accounting Firm"},
    {"category": "Finance", "name": "Tax Consulting"},
    {"category": "Finance", "name": "Financial Advisory"},
    {"category": "Finance", "name": "Insurance Agency"},
    {"category": "Finance", "name": "Mortgage Broker"},
    {"category": "Finance", "name": "Investment Firm"},
    {"category": "Finance", "name": "Credit Repair Services"},
    {"category": "Finance", "name": "Wealth Management"},
    {"category": "Finance", "name": "Loan Services (Personal, Business)"},
    {"category": "Finance", "name": "Venture Capital & Private Equity"},
    {"category": "Finance", "name": "Financial Planning"},
    {"category": "Finance", "name": "Real Estate Investment & Brokerage"},
    {"category": "Finance", "name": "Crowdfunding Platforms"},
    {"category": "Food & Beverage", "name": "Restaurant"},
    {"category": "Food & Beverage", "name": "Coffee Shop"},
    {"category": "Food & Beverage", "name": "Bakery"},
    {"category": "Food & Beverage", "name": "Ice Cream Shop"},
    {"category": "Food & Beverage", "name": "Catering Service"},
    {"category": "Food & Beverage", "name": "Food Truck"},
    {"category": "Food & Beverage", "name": "Bar & Pub"},
    {"category": "Food & Beverage", "name": "Juice Bar"},
    {"category": "Food & Beverage", "name": "Fast Food Chains"},
    {"category": "Food & Beverage", "name": "Meal Prep & Delivery"},
    {"category": "Food & Beverage", "name": "Health Food Store"},
    {"category": "Food & Beverage", "name": "Brewery or Distillery"},
    {"category": "Food & Beverage", "name": "Vegan/Organic Food"},
    {"category": "Health & Beauty", "name": "Spa"},
    {"category": "Health & Beauty", "name": "Cosmetic Clinic"},
    {"category": "Health & Beauty", "name": "Dermatology"},
    {"category": "Health & Beauty", "name": "Massage Therapy"},
    {"category": "Health & Beauty", "name": "Beauty Salon"},
    {"category": "Health & Beauty", "name": "Hair Salon"},
    {"category": "Health & Beauty", "name": "Barbershop"},
    {"category": "Health & Beauty", "name": "Nail Salon"},
    {"category": "Health & Beauty", "name": "Waxing & Skincare Services"},
    {"category": "Health & Beauty", "name": "Fitness Coaching"},
    {"category": "Health & Beauty", "name": "Weight Loss Programs"},
    {"category": "Health & Beauty", "name": "Natural Health Products"},
    {"category": "Health & Beauty", "name": "Skincare Products & Cosmetics"},
    {"category": "Health & Beauty", "name": "Wellness Retreats"},
    {"category": "Health & Beauty", "name": "Nutritional Consulting"},
    {"category": "Health & Beauty", "name": "Holistic Health Center"},
    {"category": "Health & Wellness", "name": "Fitness Center"},
    {"category": "Health & Wellness", "name": "Yoga Studio"},
    {"category": "Health & Wellness", "name": "Pharmacy"},
    {"category": "Health & Wellness", "name": "Chiropractor"},
    {"category": "Health & Wellness", "name": "Acupuncture"},
    {"category": "Health & Wellness", "name": "Mental Health Counseling"},
    {"category": "Health & Wellness", "name": "Physical Therapy"},
    {"category": "Health & Wellness", "name": "Health Insurance Broker"},
    {"category": "Health & Wellness", "name": "Nutritional Counseling"},
    {"category": "Health & Wellness", "name": "Wellness Coaching"},
    {"category": "Health & Wellness", "name": "Weight Loss Centers"},
    {"category": "Health & Wellness", "name": "Rehabilitation Centers"},
    {"category": "Home Services", "name": "Cleaning Service"},
    {"category": "Home Services", "name": "Pest Control"},
    {"category": "Home Services", "name": "Plumbing"},
    {"category": "Home Services", "name": "Electrical Services"},
    {"category": "Home Services", "name": "HVAC Services"},
    {"category": "Home Services", "name": "Interior Design"},
    {"category": "Home Services", "name": "Appliance Repair"},
    {"category": "Home Services", "name": "Lawn Care & Gardening"},
    {"category": "Home Services", "name": "Home Security Systems"},
    {"category": "Home Services", "name": "Home Automation & Smart Home"},
    {"category": "Home Services", "name": "Home Organization Services"},
    {"category": "Home Services", "name": "Renovation & Home Repair Services"},
    {"category": "Logistics", "name": "Courier Service"},
    {"category": "Logistics", "name": "Freight Forwarding"},
    {"category": "Logistics", "name": "Warehousing"},
    {"category": "Logistics", "name": "Shipping & Delivery Service"},
    {"category": "Logistics", "name": "Supply Chain Management"},
    {"category": "Logistics", "name": "Packaging & Labeling"},
    {"category": "Logistics", "name": "Import/Export Services"},
    {"category": "Logistics", "name": "Freight Brokerage"},
    {"category": "Logistics", "name": "Distribution Services"},
    {"category": "Logistics", "name": "Fleet Management"},
    {"category": "Personal Services", "name": "Hair Salon"},
    {"category": "Personal Services", "name": "Barbershop"},
    {"category": "Personal Services", "name": "Nail Salon"},
    {"category": "Personal Services", "name": "Massage Therapy"},
    {"category": "Personal Services", "name": "Personal Shopping Services"},
    {"category": "Personal Services", "name": "Personal Training"},
    {"category": "Personal Services", "name": "Life Coaching"},
    {"category": "Personal Services", "name": "Concierge Services"},
    {"category": "Personal Services", "name": "Home Organizing Services"},
    {"category": "Personal Services", "name": "Event Styling & Planning"},
    {"category": "Pet Services", "name": "Pet Grooming"},
    {"category": "Pet Services", "name": "Pet Sitting"},
    {"category": "Pet Services", "name": "Veterinary Clinic"},
    {"category": "Pet Services", "name": "Dog Training"},
    {"category": "Pet Services", "name": "Pet Supply Store"},
    {"category": "Pet Services", "name": "Animal Shelter"},
    {"category": "Pet Services", "name": "Pet Adoption Services"},
    {"category": "Pet Services", "name": "Pet Boarding"},
    {"category": "Pet Services", "name": "Pet Walking"},
    {"category": "Pet Services", "name": "Exotic Pet Care"},
    {"category": "Real Estate", "name": "Real Estate Agency"},
    {"category": "Real Estate", "name": "Property Management"},
    {"category": "Real Estate", "name": "Vacation Rentals"},
    {"category": "Real Estate", "name": "Real Estate Investment"},
    {"category": "Real Estate", "name": "Home Staging"},
    {"category": "Real Estate", "name": "Real Estate Photography"},
    {"category": "Real Estate", "name": "Commercial Real Estate"},
    {"category": "Real Estate", "name": "Real Estate Appraisal"},
    {"category": "Real Estate", "name": "Land Development"},
    {"category": "Real Estate", "name": "Vacation Home Rental Management"},
    {"category": "Real Estate", "name": "Real Estate Crowdfunding"},
    {"category": "Real Estate", "name": "Property Maintenance Services"},
    {"category": "Retail", "name": "Clothing Store"},
    {"category": "Retail", "name": "Grocery Store"},
    {"category": "Retail", "name": "Furniture Store"},
    {"category": "Retail", "name": "Electronics Store"},
    {"category": "Retail", "name": "Bookstore"},
    {"category": "Retail", "name": "Toy Store"},
    {"category": "Retail", "name": "Home Goods Store"},
    {"category": "Retail", "name": "Sports & Outdoor Equipment Store"},
    {"category": "Retail", "name": "Auto Parts & Accessories Store"},
    {"category": "Retail", "name": "Jewelry Store"},
    {"category": "Retail", "name": "DIY & Hardware Store"},
    {"category": "Retail", "name": "Luxury Goods Store"},
    {"category": "Sports & Recreation", "name": "Sports Club"},
    {"category": "Sports & Recreation", "name": "Martial Arts Studio"},
    {"category": "Sports & Recreation", "name": "Dance Studio"},
    {"category": "Sports & Recreation", "name": "Golf Course"},
    {"category": "Sports & Recreation", "name": "Ski Resort"},
    {"category": "Sports & Recreation", "name": "Adventure & Outdoor Tours"},
    {"category": "Sports & Recreation", "name": "Sports Equipment Store"},
    {"category": "Sports & Recreation", "name": "Fitness Equipment Sales & Rentals"},
    {"category": "Sports & Recreation", "name": "Swim School"},
    {"category": "Sports & Recreation", "name": "Cycling Studio"},
    {"category": "Technology", "name": "IT Consulting"},
    {"category": "Technology", "name": "Tech & IT"},
    {"category": "Technology", "name": "App Development"},
    {"category": "Technology", "name": "Cybersecurity"},
    {"category": "Technology", "name": "Tech Support"},
    {"category": "Technology", "name": "Cloud Computing"},
    {"category": "Technology", "name": "Artificial Intelligence & Machine Learning"},
    {"category": "Technology", "name": "Blockchain Development"},
    {"category": "Technology", "name": "Data Analytics & Business Intelligence"},
    {"category": "Technology", "name": "Software as a Service (SaaS)"},
    {"category": "Technology", "name": "Virtual & Augmented Reality Development"},
    {"category": "Technology", "name": "E-commerce Solutions"},
    {"category": "Technology", "name": "3D Printing & Manufacturing"},
    {"category": "Technology", "name": "IT Infrastructure Services"},
    {"category": "Travel & Tourism", "name": "Travel Agency"},
    {"category": "Travel & Tourism", "name": "Tour Operator"},
    {"category": "Travel & Tourism", "name": "Hotel"},
    {"category": "Travel & Tourism", "name": "Hostel or Airbnb Management"},
    {"category": "Travel & Tourism", "name": "Bed and Breakfast"},
    {"category": "Travel & Tourism", "name": "Vacation Planning & Consulting"},
    {"category": "Travel & Tourism", "name": "Travel Insurance Services"},
    {"category": "Travel & Tourism", "name": "Cruise Booking Services"},
    {"category": "Travel & Tourism", "name": "Travel Blogger/Influencer"},
    {"category": "Travel & Tourism", "name": "Destination Weddings"},
    {"category": "Travel & Tourism", "name": "Adventure Travel Services"},
    {"category": "Travel & Tourism", "name": "Transportation Services (Shuttles, Limousines, Taxis)"}
]

skills = [
    {"category": "Tech & IT", "name": "Coding"},
    {"category": "Tech & IT", "name": "Software Engineering"},
    {"category": "Tech & IT", "name": "Web Development"},
    {"category": "Tech & IT", "name": "Mobile Development"},
    {"category": "Tech & IT", "name": "Data Engineering"},
    {"category": "Tech & IT", "name": "Cloud Infrastructure Skills"},
    {"category": "Tech & IT", "name": "Software Architecture"},
    {"category": "Tech & IT", "name": "DataBase Administration"},
    {"category": "Tech & IT", "name": "Machine Learning & AI"},
    {"category": "Tech & IT", "name": "DevOps"},
    {"category": "Tech & IT", "name": "Blockchain"},
    {"category": "Tech & IT", "name": "Network Security"},
    {"category": "Tech & IT", "name": "Ethical Hacking"},
    {"category": "Tech & IT", "name": "Networking"},
    {"category": "Tech & IT", "name": "Cybersecurity"},
    {"category": "Tech & IT", "name": "UI/UX"},
    {"category": "Tech & IT", "name": "3D Modeling"},
    {"category": "Digital Marketing", "name": "SEO"},
    {"category": "Digital Marketing", "name": "Social Media Marketing"},
    {"category": "Digital Marketing", "name": "Content Marketing"},
    {"category": "Data Analytics", "name": "Data Visualization"},
    {"category": "Data Analytics", "name": "Tableau"},
    {"category": "Data Analytics", "name": "Power BI"},
    {"category": "Data Analytics", "name": "Statistical Modelling"},
    {"category": "Communication", "name": "Verbal Communication"},
    {"category": "Communication", "name": "Written Communication"},
    {"category": "Communication", "name": "Presentation Skills"},
    {"category": "Sales", "name": "Sales Strategies"},
    {"category": "Sales", "name": "Negotiation"},
    {"category": "Sales", "name": "Account Management"},
    {"category": "Finance", "name": "Financial Modeling"},
    {"category": "Finance", "name": "Accounting"},
    {"category": "Finance", "name": "Investment Analysis"},
    {"category": "Legal", "name": "Contract Law"},
    {"category": "Legal", "name": "Intellectual Property Law"},
    {"category": "Legal", "name": "Corporate Law"},
    {"category": "Marketing", "name": "Market Research"},
    {"category": "Marketing", "name": "Branding"},
    {"category": "Marketing", "name": "Product Marketing"},
    {"category": "Marketing", "name": "Customer Acquisition"},
    {"category": "Human Resources", "name": "Recruitment"},
    {"category": "Human Resources", "name": "Employee Relations"},
    {"category": "Human Resources", "name": "Training & Development"},
    {"category": "Human Resources", "name": "Compensation & Benefits"},
    {"category": "Management", "name": "Project Management"},
    {"category": "Management", "name": "Leadership"},
    {"category": "Management", "name": "Product Management"},
    {"category": "Management", "name": "Strategic Planning"},
    {"category": "Management", "name": "Change Management"},
    {"category": "Management", "name": "Financial Management"},
    {"category": "Management", "name": "Cost Control"},
    {"category": "Management", "name": "Cash Flow Management"},
    {"category": "Management", "name": "Market Analysis"},
    {"category": "Management", "name": "Product Innovation and Development"},
    {"category": "Management", "name": "Effective Communication"},
    {"category": "Management", "name": "Strategic Networking"},
    {"category": "Management", "name": "Empathy and Conflict Resolution"},
    {"category": "Management", "name": "Time Management"},
    {"category": "Management", "name": "Risk Management"},
    {"category": "Management", "name": "Performance Management"},
    {"category": "Engineering", "name": "Mechanical Engineering"},
    {"category": "Engineering", "name": "Electrical Engineering"},
    {"category": "Engineering", "name": "Civil Engineering"},
    {"category": "Engineering", "name": "Software Engineering"},
    {"category": "Healthcare", "name": "Patient Care"},
    {"category": "Healthcare", "name": "Specific Medical Surgery"},
    {"category": "Healthcare", "name": "General Medical Skills"},
    {"category": "Healthcare", "name": "Clinical Research"},
    {"category": "Healthcare", "name": "Pharmaceutical Skills"},
    {"category": "Healthcare", "name": "Nutrition"},
    {"category": "Healthcare", "name": "Psychology"},
    {"category": "Education", "name": "Teaching"},
    {"category": "Education", "name": "Curriculum Development"},
    {"category": "Education", "name": "E-learning"},
    {"category": "Education", "name": "Educational Technology"},
    {"category": "Hospitality", "name": "Hotel Management"},
    {"category": "Hospitality", "name": "Customer Service"},
    {"category": "Hospitality", "name": "Event Planning"},
    {"category": "Customer Support", "name": "Helpdesk"},
    {"category": "Customer Support", "name": "Technical Support"},
    {"category": "Customer Support", "name": "Client Relationship Management"},
    {"category": "Real Estate", "name": "Property Management"},
    {"category": "Real Estate", "name": "Real Estate Investment"},
    {"category": "Real Estate", "name": "Property Valuation"},
    {"category": "Real Estate", "name": "Sales & Leasing"},
    {"category": "Retail", "name": "Store Management"},
    {"category": "Retail", "name": "Inventory Management"},
    {"category": "Retail", "name": "Customer Experience"},
    {"category": "Transportation", "name": "Logistics Management"},
    {"category": "Transportation", "name": "Fleet Management"},
    {"category": "Transportation", "name": "Supply Chain Management"},
    {"category": "Transportation", "name": "Shipping & Freight"},
    {"category": "Agriculture", "name": "Crop Management"},
    {"category": "Agriculture", "name": "Livestock Management"},
    {"category": "Agriculture", "name": "Sustainability Practices"},
    {"category": "Energy", "name": "Renewable Energy"},
    {"category": "Energy", "name": "Energy Efficiency"},
    {"category": "Energy", "name": "Energy Consulting"},
    {"category": "Construction", "name": "Project Planning"},
    {"category": "Construction", "name": "Building Information Modeling"},
    {"category": "Construction", "name": "Site Management"},
    {"category": "Logistics", "name": "Freight Forwarding"},
    {"category": "Logistics", "name": "Courier Services"},
    {"category": "Logistics", "name": "Warehousing"},
    {"category": "Logistics", "name": "Inventory Control"},
    {"category": "Sports", "name": "Coaching"},
    {"category": "Sports", "name": "Sports Nutrition"},
    {"category": "Sports", "name": "Fitness Training"},
    {"category": "Tourism", "name": "Tourism Management"},
    {"category": "Tourism", "name": "Travel Planning"},
    {"category": "Tourism", "name": "Tour Guiding"},
    {"category": "Tourism", "name": "Hospitality Management"},
    {"category": "Finance", "name": "Taxation"},
    {"category": "Finance", "name": "Auditing"},
    {"category": "Finance", "name": "Financial Analysis"},
    {"category": "Personal Development", "name": "Self-Discipline"},
    {"category": "Personal Development", "name": "Emotional Intelligence"},
    {"category": "Personal Development", "name": "Mindfulness"},
    {"category": "Personal Development", "name": "Stress Management"},
    {"category": "Manual & Craft Skills", "name": "Woodworking"},
    {"category": "Manual & Craft Skills", "name": "Carpentry"},
    {"category": "Manual & Craft Skills", "name": "Masonry"},
    {"category": "Manual & Craft Skills", "name": "Welding"},
    {"category": "Manual & Craft Skills", "name": "Metalworking"},
    {"category": "Manual & Craft Skills", "name": "Plumbing"},
    {"category": "Manual & Craft Skills", "name": "Electrical Wiring"},
    {"category": "Manual & Craft Skills", "name": "Drywall Installation"},
    {"category": "Manual & Craft Skills", "name": "Painting & Decorating"},
    {"category": "Manual & Craft Skills", "name": "Roofing"},
    {"category": "Manual & Craft Skills", "name": "Tile Setting"},
    {"category": "Manual & Craft Skills", "name": "Sewing & Tailoring"},
    {"category": "Manual & Craft Skills", "name": "Car Repair"},
    {"category": "Manual & Craft Skills", "name": "Gardening & Landscaping"},
    {"category": "Manual & Craft Skills", "name": "Construction"},
    {"category": "Food & Beverage", "name": "Baking"},
    {"category": "Food & Beverage", "name": "Butchery"},
    {"category": "Food & Beverage", "name": "Food Safety & Sanitation"},
    {"category": "Food & Beverage", "name": "Menu Planning"},
    {"category": "Food & Beverage", "name": "Food Preparation & Cooking Techniques"},
    {"category": "Food & Beverage", "name": "Bartending"},
    {"category": "Food & Beverage", "name": "Wine Knowledge & Pairing"},
    {"category": "Food & Beverage", "name": "Cocktail Mixing"},
    {"category": "Food & Beverage", "name": "Catering & Event Planning"},
    {"category": "Food & Beverage", "name": "Pastry and Chocolate"},
    {"category": "Arts", "name": "Drawing & Illustration"},
    {"category": "Arts", "name": "Painting Techniques"},
    {"category": "Arts", "name": "Sculpture"},
    {"category": "Arts", "name": "Digital Art & Design"},
    {"category": "Arts", "name": "Graphic Design"},
    {"category": "Arts", "name": "Photography"},
    {"category": "Arts", "name": "Ceramics & Pottery"},
    {"category": "Arts", "name": "Film Production & Editing"},
    {"category": "Arts", "name": "Music Composition & Arrangement"},
    {"category": "Arts", "name": "Dance Choreography"},
    {"category": "Arts", "name": "Theater Performance"},
    {"category": "Arts", "name": "Creative Writing & Poetry"},
    {"category": "Arts", "name": "Performance Art"},
    {"category": "Arts", "name": "Crafting & Jewelry Making"},
    {"category": "Arts", "name": "Landscaping Design"},
    {"category": "Arts", "name": "Building Design"},


]

hobbies = [
  { "category": "Sports", "name": "Soccer" }, 
  { "category": "Sports", "name": "Rugby" }, 
  { "category": "Sports", "name": "American football" },
  { "category": "Sports", "name": "Baseball" }, 
  { "category": "Sports and Fitness", "name": "Volleyball" },
  { "category": "Sports and Fitness", "name": "Basketball" }, 
  { "category": "Sports and Fitness", "name": "Swimming" }, 
  { "category": "Sports and Fitness", "name": "Cycling" }, 
  { "category": "Sports and Fitness", "name": "Tennis & Padel" }, 
  { "category": "Sports and Fitness", "name": "Yoga" }, 
  { "category": "Sports and Fitness", "name": "Running" }, 
  { "category": "Sports and Fitness", "name": "Skiing" }, 
  { "category": "Sports and Fitness", "name": "Figthing" }, 
  { "category": "Sports and Fitness", "name": "Weight Lifting" }, 
  { "category": "Sports and Fitness", "name": "Dancing" },
  { "category": "Music", "name": "Playing an instrument" }, 
  { "category": "Music", "name": "Singing" }, 
  { "category": "Music", "name": "Composing music" }, 
  { "category": "Music", "name": "Listening to music" }, 
  { "category": "Music", "name": "DJing" }, 
  { "category": "Music", "name": "Music production" }, 
  { "category": "Arts and Crafts", "name": "Drawing" }, 
  { "category": "Arts and Crafts", "name": "Painting" }, 
  { "category": "Arts and Crafts", "name": "Photography" }, 
  { "category": "Arts and Crafts", "name": "Pottery" }, 
  { "category": "Arts and Crafts", "name": "Knitting" }, 
  { "category": "Arts and Crafts", "name": "Embroidery" }, 
  { "category": "Arts and Crafts", "name": "Sculpting" }, 
  { "category": "Arts and Crafts", "name": "Acting" }, 
  { "category": "Outdoor Activities", "name": "Camping" }, 
  { "category": "Outdoor Activities", "name": "Hiking" }, 
  { "category": "Outdoor Activities", "name": "Fishing" }, 
  { "category": "Outdoor Activities", "name": "Rock climbing" }, 
  { "category": "Outdoor Activities", "name": "Gardening" }, 
  { "category": "Outdoor Activities", "name": "Birdwatching" }, 
  { "category": "Outdoor Activities", "name": "Geocaching" }, 
  { "category": "Outdoor Activities", "name": "Cycling" }, 
  { "category": "Outdoor Activities", "name": "Boating" }, 
  { "category": "Outdoor Activities", "name": "Backpacking" }, 
  { "category": "Collecting", "name": "Stamp collecting" }, 
  { "category": "Collecting", "name": "Coin collecting" }, 
  { "category": "Collecting", "name": "Toy collecting" }, 
  { "category": "Collecting", "name": "Comic book collecting" }, 
  { "category": "Collecting", "name": "Antique collecting" }, 
  { "category": "Collecting", "name": "Action figure collecting" }, 
  { "category": "Collecting", "name": "Art collecting" }, 
  { "category": "Collecting", "name": "Music collecting" }, 
  { "category": "Technology", "name": "Coding" }, 
  { "category": "Technology", "name": "Robotics" }, 
  { "category": "Technology", "name": "3D printing" }, 
  { "category": "Technology", "name": "Virtual reality" }, 
  { "category": "Technology", "name": "Drone flying" }, 
  { "category": "Technology", "name": "Electronics tinkering" }, 
  { "category": "Food and Drink", "name": "Cooking" }, 
  { "category": "Food and Drink", "name": "Baking" }, 
  { "category": "Food and Drink", "name": "Wine tasting" }, 
  { "category": "Food and Drink", "name": "Beer brewing" }, 
  { "category": "Food and Drink", "name": "Coffee brewing" },
  { "category": "Health", "name": "Meditation" },
  { "category": "Health", "name": "Mental wellness" },
  { "category": "Health", "name": "Mindfulness" },
  { "category": "Health", "name": "Healthy eating" },
  { "category": "Entertainment", "name": "Cinema" },
  { "category": "Entertainment", "name": "Series" },
  { "category": "Entertainment", "name": "Anime" },
  { "category": "Entertainment", "name": "Theater" },
  { "category": "Entertainment", "name": "Podcast" },
  { "category": "Entertainment", "name": "Parties" },
  { "category": "Game", "name": "Video Games" },
  { "category": "Game", "name": "Board Games" },
  { "category": "Game", "name": "Role-playing games" },
  { "category": "Travelling", "name": "Festivals" },
  { "category": "Travelling", "name": "Luxury travel" },
  { "category": "Travelling", "name": "Road trips" },
  { "category": "Travelling", "name": "Cruise travel" },
  { "category": "Travelling", "name": "Cultural travel" },
  { "category": "Travelling", "name": "Backpacking" },
  { "category": "Travelling", "name": "Adventure travel" },
  { "category": "Social Media and Networking", "name": "Blogging" },
  { "category": "Social Media and Networking", "name": "Vlogging" },
  { "category": "Social Media and Networking", "name": "Content creation" },
  { "category": "Social Media and Networking", "name": "Podcasting" },
  { "category": "Literature", "name": "Reading comics and manga" },
  { "category": "Literature", "name": "Reading books" },
  { "category": "Literature", "name": "Reading poetry" },
  { "category": "Literature", "name": "Creative Writing" },
  { "category": "Literature", "name": "Journaling" },



]
 



def publishCategories(connection, categoryArray:list, nodesLabel:str ):
    x = 0
    for business in categoryArray:
        category = business["category"]
        name = business["name"]
        query = f"""
        CREATE (c:{nodesLabel}{{category: '{category}', name: '{name}'}})
        """
        result = connection.run_query(query)
        print(x, 'OK')
        connection.close()
        x += 1

URI = os.getenv("NEO4J_URI") + "/:7687" 
AUTH = {
    "user": os.getenv("NEO4J_USERNAME"),
    "password": os.getenv("NEO4J_PASSWORD"),
}
connection = Neo4jManager(URI, AUTH)
connection.connect()

#publishCategories(connection=connection, categoryArray=businesses, nodesLabel="BusinessType")
#publishCategories(connection=connection, categoryArray=skills, nodesLabel="Skill")
publishCategories(connection=connection, categoryArray=hobbies, nodesLabel="Hobbie")