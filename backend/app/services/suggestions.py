SUGGESTION_MAP = {

    "python":
    "Improve Python by building real-world projects",

    "sql":
    "Practice advanced SQL queries, joins, CTEs and window functions",

    "machine learning":
    "Build end-to-end Machine Learning projects using real datasets",

    "deep learning":
    "Learn neural networks and Deep Learning architectures",

    "nlp":
    "Build NLP projects such as chatbots, sentiment analysis and text classification",

    "tensorflow":
    "Build Deep Learning projects using TensorFlow",

    "pytorch":
    "Learn PyTorch and implement neural network models",

    "pandas":
    "Practice data cleaning, analysis and feature engineering using Pandas",

    "numpy":
    "Strengthen numerical computing skills using NumPy",

    "scikit-learn":
    "Build Machine Learning pipelines using Scikit-Learn",

    "tableau":
    "Create interactive dashboards using Tableau",

    "power bi":
    "Build business intelligence dashboards using Power BI",

    "aws":
    "Deploy Machine Learning applications using AWS services",

    "docker":
    "Containerize Machine Learning projects using Docker",

    "git":
    "Practice version control and collaborative development using Git",

    "linux":
    "Improve Linux command line and server management skills",

    "java":
    "Build object-oriented applications using Java",

    "c++":
    "Practice data structures and algorithms using C++",

    "javascript":
    "Build interactive web applications using JavaScript",

    "html":
    "Strengthen frontend development using HTML",

    "css":
    "Improve responsive web design using CSS",

    "react":
    "Build modern frontend applications using React",

    "node.js":
    "Develop backend APIs using Node.js"
}


def generate_suggestions(missing_skills):

    suggestions = []

    for skill in missing_skills:

        if skill in SUGGESTION_MAP:

            suggestions.append(
                SUGGESTION_MAP[skill]
            )

        else:

            suggestions.append(
                f"Learn and gain practical experience in {skill}"
            )

    return suggestions