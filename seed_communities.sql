--seed_communities
BEGIN TRANSACTION;

DELETE FROM Communities;

INSERT INTO Communities (name, description) VALUES
('Software Engineering', 'Discuss software development, internships, hackathons, and system design'),
('Finance', 'Banking, investing, corporate finance, and markets'),
('Consulting', 'Case prep, firm insights, and networking tips'),
('Extracurriculars', 'Clubs, sports, volunteering, and Yale campus life'),
('Data Science', 'Analytics, machine learning, data visualization, and big data'),
('Public Policy', 'Government, non‑profit policy analysis and advocacy'),
('Entrepreneurship', 'Startups, innovation, funding, and pitch practice'),
('Pre‑Med & Healthcare', 'Medical school prep, healthcare careers, and clinical volunteering'),
('Arts & Design', 'Visual and performing arts, graphic design, and creativity'),
('Law & Public Interest', 'Law school prep, public interest law, and social justice'),
('Others', 'Miscellaneous topics and general discussions');

COMMIT;
