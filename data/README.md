# Dataset Specifications & Schema Mapping

This directory contains datasets explored during the initial research phase of the project. These datasets were studied to better understand resume structures, formatting differences, and how candidate information may be organized for information extraction.

---

# 1. Dataset Overview

## 1.1 Kaggle Structured Resume Dataset

### Format

CSV files (`people.csv`, `education.csv`, `skills.csv`)

### Structure

A structured relational dataset containing candidate information organized across multiple linked tables.

### Observations

* Candidate information is divided into separate tables for personal details, education, and skills.
* `person_id` acts as a common linking field between records.
* The dataset helped in understanding how resume information can be stored in a structured database format.
* It also provided ideas for organizing extracted resume information into structured JSON or database-friendly formats.

### Relevance to the Project

Since resumes contain multiple categories of information such as education, experience, skills, certifications, and achievements, understanding structured data organization was useful for planning information extraction.

---

## 1.2 PDF Resume Dataset

### Format

Collection of PDF resumes organized by job category (Data Science, HR, Java Developer, Accountant, etc.)

### Structure

Unstructured resumes with different layouts, section ordering, fonts, and formatting styles.

### Observations

* Resume layouts vary significantly from person to person.
* Section names and ordering are inconsistent across resumes.
* Some resumes are short and industry-focused, while others contain detailed projects and work experience.
* Longer academic or research-oriented resumes often include additional sections such as publications, certifications, workshops, teaching experience, and research contributions.

### Relevance to the Project

These variations highlighted the difficulty of building a single resume parsing approach for all document types and reinforced the need for flexible information extraction methods.

---

# 2. Difference Between Academic CVs and Corporate Resumes

During the exploration phase, noticeable structural differences between corporate resumes and academic CVs were identified.

| Attribute               | Corporate Resume                     | Academic CV                                   |
| ----------------------- | ------------------------------------ | --------------------------------------------- |
| **Typical Length**      | 1–2 pages                            | 5–10+ pages                                   |
| **Primary Focus**       | Work experience, projects, skills    | Qualifications, research, publications        |
| **Key Information**     | Tools, technologies, business impact | Research work, journals, teaching experience  |
| **Education Details**   | Brief degree summary                 | Detailed academic background                  |
| **Additional Sections** | Certifications, projects             | Publications, workshops, patents, memberships |

### Observation

Traditional resume parsing methods are generally optimized for short corporate resumes. Academic CVs are more detailed and may require additional handling due to their structure and content.

---

# 3. Planned Schema Mapping

Based on project requirements, the following information categories were identified for extraction from resumes:

* **Personal Details** → Name, date of birth, age, contact information
* **Education History** → Degree, institution, passing year, CGPA/percentage
* **Experience** → Teaching, research, internship, or industry experience
* **Projects & Research Work** → Projects, thesis work, research contributions
* **Publications** → Journal papers, conference papers, research work
* **Skills & Certifications** → Technical skills, certifications, workshops

### Purpose

The extracted information is intended to be converted into a structured format to support easier candidate evaluation and reduce manual effort during the recruitment process.
