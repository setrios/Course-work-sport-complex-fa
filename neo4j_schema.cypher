// SportComplex Neo4j Schema & Sample Data

// ==========================================
// 1. CONSTRAINTS & INDEXES
// ==========================================

CREATE CONSTRAINT client_id IF NOT EXISTS FOR (c:Client) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT trainer_id IF NOT EXISTS FOR (t:Trainer) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT service_id IF NOT EXISTS FOR (s:Service) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT product_id IF NOT EXISTS FOR (p:Product) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT session_id IF NOT EXISTS FOR (ts:TrainingSession) REQUIRE ts.id IS UNIQUE;

// ==========================================
// 2. NODE CREATION (Templates)
// ==========================================

// Create Clients
CREATE (:Client {
  id: 1,
  name: "Ivan Petrenko",
  registration_date: date("2024-01-15"),
  total_visits: 145,
  total_spent: 12500.00,
  preferred_time: "evening",
  fitness_level: "intermediate"
});

// Create Trainers
CREATE (:Trainer {
  id: 1,
  name: "Oleksii Kovalenko",
  specialization: "gym",
  experience_years: 8,
  avg_rating: 4.8,
  total_sessions: 856,
  hourly_rate: 600.00
});

// Create Services
CREATE (:Service {id: 1, name: "Swimming Pool", category: "water", base_price: 150.00});
CREATE (:Service {id: 2, name: "Gym", category: "fitness", base_price: 100.00});

// Create Products
CREATE (:Product {
  id: 45,
  article_number: "NP-WHEY-1000",
  name: "Whey Protein 1kg",
  category: "nutrition",
  price: 850.00,
  brand: "NutritionPro"
});

// ==========================================
// 3. RELATIONSHIPS
// ==========================================

// Client Interactions
MATCH (c:Client {id: 1}), (s:Service {id: 1})
CREATE (c)-[:VISITED {
  date: date("2024-12-01"),
  duration_minutes: 60,
  satisfaction_rating: 5
}]->(s);

MATCH (c:Client {id: 1}), (p:Product {id: 45})
CREATE (c)-[:PURCHASED {
  date: date("2024-12-05"),
  quantity: 1,
  total_amount: 850.00
}]->(p);

// Trainer Interactions
MATCH (t:Trainer {id: 1}), (s:Service {id: 2})
CREATE (t)-[:SPECIALIZES_IN]->(s);

// Product Recommendations (Similarity)
MATCH (p1:Product {id: 45}), (s:Service {id: 2})
CREATE (p1)-[:RECOMMENDED_FOR {
  relevance_score: 0.9,
  reason: "recovery"
}]->(s);

// ==========================================
// 4. SAMPLE QUERIES
// ==========================================

// Recommend services based on similar clients
// MATCH (c:Client {id: 1})-[:SIMILAR_TO]-(similar:Client)
// MATCH (similar)-[:VISITED]->(s:Service)
// WHERE NOT (c)-[:VISITED]->(s)
// RETURN s.name, COUNT(*) as recommendations
// ORDER BY recommendations DESC;

// Find best trainer for a client
// MATCH (c:Client {id: 1})-[:SIMILAR_TO]-(similar:Client)
// MATCH (similar)-[r:TRAINED_BY WHERE r.rating >= 4.5]->(t:Trainer)
// RETURN t.name, AVG(r.rating) as avg_rating
// ORDER BY avg_rating DESC;
