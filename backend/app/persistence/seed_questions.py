"""
Seed script for interview questions.
Run: python -m app.persistence.seed_questions
"""
import json
from sqlmodel import Session
from app.persistence.database import engine
from app.models.schemas import Question, QuestionType, Questionnaire

# ============ AI-ML Questions ============
AI_ML_QUESTIONS = [
    {
        "domain": "AI-ML",
        "question_text": "What is the primary purpose of a loss function in machine learning?",
        "question_type": QuestionType.MCQ,
        "options": json.dumps([
            "To measure model accuracy",
            "To quantify prediction error for optimization",
            "To regularize the model",
            "To preprocess data"
        ]),
        "correct_option": 1,
        "time_limit_sec": 60
    },
    {
        "domain": "AI-ML",
        "question_text": "Which algorithm is best suited for high-dimensional sparse data classification?",
        "question_type": QuestionType.MCQ,
        "options": json.dumps([
            "Decision Tree",
            "K-Nearest Neighbors",
            "Support Vector Machine (SVM)",
            "Naive Bayes"
        ]),
        "correct_option": 2,
        "time_limit_sec": 60
    },
    {
        "domain": "AI-ML",
        "question_text": "What does 'overfitting' mean in machine learning?",
        "question_type": QuestionType.MCQ,
        "options": json.dumps([
            "Model performs well on training data but poorly on new data",
            "Model performs poorly on all data",
            "Model takes too long to train",
            "Model uses too much memory"
        ]),
        "correct_option": 0,
        "time_limit_sec": 60
    },
    {
        "domain": "AI-ML",
        "question_text": "Explain the difference between supervised and unsupervised learning. Provide examples of each.",
        "question_type": QuestionType.VIDEO,
        "time_limit_sec": 120
    },
    {
        "domain": "AI-ML",
        "question_text": "Describe a machine learning project you've worked on. What was the problem, approach, and outcome?",
        "question_type": QuestionType.VIDEO,
        "time_limit_sec": 180
    },
    {
        "domain": "AI-ML",
        "question_text": "What is gradient descent? Explain briefly how it works.",
        "question_type": QuestionType.AUDIO,
        "time_limit_sec": 90
    },
    {
        "domain": "AI-ML",
        "question_text": "Which of these is NOT a neural network activation function?",
        "question_type": QuestionType.MCQ,
        "options": json.dumps([
            "ReLU",
            "Sigmoid",
            "Softmax",
            "Gradient"
        ]),
        "correct_option": 3,
        "time_limit_sec": 60
    },
    {
        "domain": "AI-ML",
        "question_text": "What is the purpose of dropout in neural networks?",
        "question_type": QuestionType.MCQ,
        "options": json.dumps([
            "Speed up training",
            "Reduce overfitting by randomly disabling neurons",
            "Increase model size",
            "Normalize inputs"
        ]),
        "correct_option": 1,
        "time_limit_sec": 60
    },
    {
        "domain": "AI-ML",
        "question_text": "Write pseudocode for a binary search algorithm.",
        "question_type": QuestionType.TEXT,
        "time_limit_sec": 180
    },
    {
        "domain": "AI-ML",
        "question_text": "How would you handle class imbalance in a classification dataset? Describe at least two techniques.",
        "question_type": QuestionType.VIDEO,
        "time_limit_sec": 120
    }
]

# ============ Fullstack Questions ============
FULLSTACK_QUESTIONS = [
    {
        "domain": "Fullstack",
        "question_text": "What does REST stand for?",
        "question_type": QuestionType.MCQ,
        "options": json.dumps([
            "Remote Execution State Transfer",
            "Representational State Transfer",
            "Request State Transformation",
            "Resource Exchange Standard"
        ]),
        "correct_option": 1,
        "time_limit_sec": 60
    },
    {
        "domain": "Fullstack",
        "question_text": "Which HTTP method is idempotent?",
        "question_type": QuestionType.MCQ,
        "options": json.dumps([
            "POST",
            "PATCH",
            "PUT",
            "None of the above"
        ]),
        "correct_option": 2,
        "time_limit_sec": 60
    },
    {
        "domain": "Fullstack",
        "question_text": "What is the primary purpose of a CDN (Content Delivery Network)?",
        "question_type": QuestionType.MCQ,
        "options": json.dumps([
            "Database replication",
            "Serve static content from geographically distributed servers",
            "Encrypt API requests",
            "Manage user sessions"
        ]),
        "correct_option": 1,
        "time_limit_sec": 60
    },
    {
        "domain": "Fullstack",
        "question_text": "Explain the request-response cycle in a typical web application.",
        "question_type": QuestionType.VIDEO,
        "time_limit_sec": 120
    },
    {
        "domain": "Fullstack",
        "question_text": "Describe your experience with databases. When would you choose SQL vs NoSQL?",
        "question_type": QuestionType.VIDEO,
        "time_limit_sec": 150
    },
    {
        "domain": "Fullstack",
        "question_text": "What is CORS and why is it important for web security?",
        "question_type": QuestionType.AUDIO,
        "time_limit_sec": 90
    },
    {
        "domain": "Fullstack",
        "question_text": "Which is NOT a valid CSS selector?",
        "question_type": QuestionType.MCQ,
        "options": json.dumps([
            ".class-name",
            "#element-id",
            "@media-query",
            "[data-attribute]"
        ]),
        "correct_option": 2,
        "time_limit_sec": 60
    },
    {
        "domain": "Fullstack",
        "question_text": "What is the Virtual DOM and why is it used in frameworks like React?",
        "question_type": QuestionType.MCQ,
        "options": json.dumps([
            "A database for virtual reality applications",
            "An in-memory representation of the real DOM for efficient updates",
            "A CSS optimization technique",
            "A browser security feature"
        ]),
        "correct_option": 1,
        "time_limit_sec": 60
    },
    {
        "domain": "Fullstack",
        "question_text": "Write a SQL query to find all duplicate email addresses in a 'users' table.",
        "question_type": QuestionType.TEXT,
        "time_limit_sec": 180
    },
    {
        "domain": "Fullstack",
        "question_text": "How do you optimize frontend performance? Mention at least 3 techniques.",
        "question_type": QuestionType.VIDEO,
        "time_limit_sec": 120
    }
]

# ============ Cybersecurity Questions ============
CYBERSEC_QUESTIONS = [
    {
        "domain": "Cybersecurity",
        "question_text": "What does CIA stand for in information security?",
        "question_type": QuestionType.MCQ,
        "options": json.dumps([
            "Central Intelligence Agency",
            "Confidentiality, Integrity, Availability",
            "Computer Infrastructure Analysis",
            "Critical Information Assets"
        ]),
        "correct_option": 1,
        "time_limit_sec": 60
    },
    {
        "domain": "Cybersecurity",
        "question_text": "Which type of attack exploits user trust to gain access?",
        "question_type": QuestionType.MCQ,
        "options": json.dumps([
            "Brute Force",
            "SQL Injection",
            "Social Engineering",
            "Buffer Overflow"
        ]),
        "correct_option": 2,
        "time_limit_sec": 60
    },
    {
        "domain": "Cybersecurity",
        "question_text": "What is the primary purpose of a firewall?",
        "question_type": QuestionType.MCQ,
        "options": json.dumps([
            "Encrypt data in transit",
            "Filter network traffic based on rules",
            "Store passwords securely",
            "Detect malware"
        ]),
        "correct_option": 1,
        "time_limit_sec": 60
    },
    {
        "domain": "Cybersecurity",
        "question_text": "Explain the difference between symmetric and asymmetric encryption.",
        "question_type": QuestionType.VIDEO,
        "time_limit_sec": 120
    },
    {
        "domain": "Cybersecurity",
        "question_text": "Describe a security vulnerability you've identified or helped fix. What was your approach?",
        "question_type": QuestionType.VIDEO,
        "time_limit_sec": 180
    },
    {
        "domain": "Cybersecurity",
        "question_text": "What is SQL injection and how do you prevent it?",
        "question_type": QuestionType.AUDIO,
        "time_limit_sec": 90
    },
    {
        "domain": "Cybersecurity",
        "question_text": "Which protocol provides secure web communication?",
        "question_type": QuestionType.MCQ,
        "options": json.dumps([
            "HTTP",
            "FTP",
            "HTTPS/TLS",
            "SMTP"
        ]),
        "correct_option": 2,
        "time_limit_sec": 60
    },
    {
        "domain": "Cybersecurity",
        "question_text": "What is a zero-day vulnerability?",
        "question_type": QuestionType.MCQ,
        "options": json.dumps([
            "A vulnerability discovered on day zero of a project",
            "A vulnerability with no known patch at time of discovery",
            "A vulnerability that takes zero days to exploit",
            "A vulnerability in legacy systems"
        ]),
        "correct_option": 1,
        "time_limit_sec": 60
    },
    {
        "domain": "Cybersecurity",
        "question_text": "List at least 3 best practices to secure a REST API.",
        "question_type": QuestionType.TEXT,
        "time_limit_sec": 180
    },
    {
        "domain": "Cybersecurity",
        "question_text": "How would you respond to and investigate a suspected data breach?",
        "question_type": QuestionType.VIDEO,
        "time_limit_sec": 150
    }
]


def seed_questions():
    """Seed all questions into the database."""
    with Session(engine) as session:
        # Check if already seeded
        existing = session.query(Question).first()
        if existing:
            print("Questions already seeded. Skipping...")
            return
        
        all_questions = AI_ML_QUESTIONS + FULLSTACK_QUESTIONS + CYBERSEC_QUESTIONS
        
        for q_data in all_questions:
            question = Question(**q_data)
            session.add(question)
        
        session.commit()
        print(f"Successfully seeded {len(all_questions)} questions!")


def seed_questionnaires():
    """Create default questionnaires for demo jobs."""
    with Session(engine) as session:
        # AI-ML questionnaire (questions 1-10)
        ai_ml = Questionnaire(
            job_id=1,  # Assuming job ID 1 is AI-ML role
            name="AI-ML Technical Assessment",
            question_ids="1,2,3,4,5,6,7,8,9,10"
        )
        
        # Fullstack questionnaire (questions 11-20)
        fullstack = Questionnaire(
            job_id=2,  # Assuming job ID 2 is Fullstack role
            name="Fullstack Developer Assessment",
            question_ids="11,12,13,14,15,16,17,18,19,20"
        )
        
        # Cybersec questionnaire (questions 21-30)
        cybersec = Questionnaire(
            job_id=3,  # Assuming job ID 3 is Cybersec role
            name="Cybersecurity Assessment",
            question_ids="21,22,23,24,25,26,27,28,29,30"
        )
        
        session.add_all([ai_ml, fullstack, cybersec])
        session.commit()
        print("Successfully created 3 questionnaires!")


if __name__ == "__main__":
    seed_questions()
    seed_questionnaires()
