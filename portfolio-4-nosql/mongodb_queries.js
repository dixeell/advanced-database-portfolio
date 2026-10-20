// Run in mongosh (UNTESTED here: no MongoDB server in the build sandbox; the same logic
// is verified in run_portfolio4.py). Import first:
//   mongoimport --db university --collection students --file output/students.json
use university

db.students.createIndex({ "programme.name": 1, cgpa: -1 })
db.students.createIndex({ email: 1 }, { unique: true })

// Q1 transcript: single read, no joins (results are embedded)
db.students.findOne({ _id: "MIT/2025/01234" }, { name: 1, results: 1, cgpa: 1 })

// Q2 average CGPA per programme
db.students.aggregate([
  { $match: { cgpa: { $ne: null } } },
  { $group: { _id: "$programme.name", avgCgpa: { $avg: "$cgpa" }, students: { $sum: 1 } } },
  { $sort: { avgCgpa: -1 } }
])

// Q3 students with at least one F
db.students.countDocuments({ "results.grade": "F" })

// Q4 course-level fail rate (unwind the embedded array)
db.students.aggregate([
  { $unwind: "$results" },
  { $group: { _id: "$results.course_code", n: { $sum: 1 },
              fails: { $sum: { $cond: [{ $eq: ["$results.grade", "F"] }, 1, 0] } } } },
  { $project: { failPct: { $multiply: [{ $divide: ["$fails", "$n"] }, 100] } } },
  { $sort: { failPct: -1 } }, { $limit: 5 }
])
