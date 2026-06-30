# Project Scope: Faculty Recruitment Portal (AI Resume Parsing System)
**Student Name:** [Your Name] | **Enrollment No:** [Your Enrollment Number]  
**Organization:** JK Lakshmipat University, Jaipur  
**Course Code:** PS1101 (Practice School I)

## 1. Project Objective
The objective of this project is to build an automated, web-based Faculty Recruitment Portal that parses submitted resumes and CVs, extracts key academic and professional attributes, and structures them into standardized candidate profiles. This tool will streamline the initial candidate screening workflow by replacing manual reading with intelligent digital extraction.

## 2. Key Extraction Targets
Faculty CVs differ substantially from standard corporate resumes. The portal must successfully identify and extract the following core sections:
- **Name & Title:** Candidate name, including academic prefixes like Dr. or Prof.
- **Contact Details:** Email addresses, mobile/telephone numbers, and professional links (e.g., LinkedIn, Google Scholar, ORCID).
- **Academic Qualifications:** Ph.D., Master's (M.Tech., M.Sc., MBA), and Bachelor's (B.E., B.Tech.) degrees, along with specializing branches, graduating institutes, universities, passing years, and corresponding CGPA or percentage marks.
- **Research Publications:** Academic papers published in journals and conferences (including titles, authors, years, and venues).
- **Professional Experience:** Detailed records of teaching, research, and industrial roles (including designations, employers, and employment durations).
- **Skills & Competencies:** Core technical skills, programming languages, and academic methodologies.
- **Additional Achievements:** Patents, consultancy projects, book publications, dissertations guided, professional memberships, and extracurricular highlights.

## 3. Understanding the Faculty Hiring Workflow
The standard academic hiring workflow at JKLU consists of the following stages:
1. **Advertisement Release:** The HR department publishes announcements for vacant faculty positions.
2. **Application Collection:** Resumes are submitted through email, paper hand-ins, or portal uploads.
3. **Manual Review:** An expert committee reads each multi-page CV (often 5 to 10 pages long) to verify whether the applicant meets the eligibility criteria (e.g., Ph.D. status, publication count, teaching load).
4. **Shortlisting:** Eligible candidates are invited for technical presentations and viva interviews.

## 4. Problems with Manual Screening
- **Extremely Time-Consuming:** Academic CVs are exceptionally dense, containing extensive publication lists and detailed project descriptions. A human reviewer takes 10 to 15 minutes per resume.
- **Formatting Inconsistency:** CVs are received in varied formats (digital PDFs, scanned image-based PDFs, and MS Word documents) without a standard layout.
- **High Error Rate:** Reviewers can easily miss critical qualifications, publication citations, or patent listings buried deep in a multi-page document.

## 5. Why a Custom Portal is Needed
Most corporate Applicant Tracking Systems (ATS) are optimized for industry resumes. They search for specific commercial job titles and skill keywords but completely ignore academic credentials like journal publication types, teaching records, and doctoral research guidance. A custom portal addresses these academic-specific needs, normalizing different layouts into a single database schema and generating a uniform candidate summary.

## 6. Expected Deliverables (End of Internship)
- **Interactive Frontend:** A drag-and-drop web dashboard for resume uploads and parsed result previewing.
- **Flask Backend API:** A robust Python backend routing files, checking searchability, extracting text, running the NLP engine, and storing results.
- **ReportLab PDF Generator:** A module that converts parsed JSON records into an official, standardized "Application Form for Faculty Position" PDF document for the selection committee.
