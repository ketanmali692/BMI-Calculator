# BMI Calculator - Advanced Tier

A Python GUI application to calculate Body Mass Index (BMI) with multi-user support, database storage, and trend visualization.

---

## ✨ Features

- 🖥️ **GUI** built with Tkinter
- 📊 **BMI calculation** using formula: BMI = weight / (height²)
- 🎨 **Color-coded results**:
  - 🔵 Underweight (< 18.5) — Blue
  - 🟢 Normal (18.5 – 24.9) — Green
  - 🟠 Overweight (25 – 29.9) — Orange
  - 🔴 Obese (≥ 30) — Red
- 👥 **Multi-user support** (named users)
- 💾 **SQLite database** storage
- 📈 **BMI trend graph** using matplotlib
- 📋 **View all records** in a table
- ⚠️ **Input validation**
- 🔴 **Error handling** for database failures

---

## 🛠️ Installation

### 1. Install dependencies

```bash
pip install -r requirements.txt