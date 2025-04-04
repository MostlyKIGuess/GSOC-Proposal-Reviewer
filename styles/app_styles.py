def get_app_styles():
    return """
    <style>
        .main {
            background-color: #121212;
            color: #e0e0e0;
            font-family: 'Arial', sans-serif;
        }
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .feedback-box {
            background-color: #1e1e1e;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            margin-top: 20px;
            color: #e0e0e0;
        }
        .score-display {
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        .high-score {
            background-color: #1e4620;
            color: #4caf50;
        }
        .medium-score {
            background-color: #332d15;
            color: #ffeb3b;
        }
        .low-score {
            background-color: #391c1c;
            color: #f44336;
        }
        .header-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        .logo-text {
            font-size: 2.5rem;
            font-weight: bold;
            margin-right: 10px;
            color: #e0e0e0;
        }
        .metrics-container {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin: 20px 0;
        }
        .metric-card {
            background-color: #1e1e1e;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            text-align: center;
        }
        .metric-title {
            font-size: 16px;
            color: #bdbdbd;
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #e0e0e0;
        }
        .timeline {
            background-color: #1e1e1e;
            border-radius: 10px;
            padding: 15px;
            margin-top: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }
        .timeline-item {
            padding: 10px;
            border-left: 2px solid #4caf50;
            margin-left: 20px;
            margin-bottom: 10px;
            position: relative;
            color: #e0e0e0;
        }
        .timeline-item::before {
            content: "";
            position: absolute;
            width: 12px;
            height: 12px;
            background-color: #4caf50;
            border-radius: 50%;
            left: -7px;
            top: 15px;
        }
        .key-points {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 20px;
        }
        .key-point {
            background-color: #1e2f1e;
            border-radius: 10px;
            padding: 15px;
            border-left: 4px solid #4caf50;
            color: #e0e0e0;
            margin-bottom: 10px;
        }
        .feedback-section {
            margin: 15px 0;
        }
        .feedback-header {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #e0e0e0;
        }
        .tag {
            display: inline-block;
            background-color: #333333;
            color: #e0e0e0;
            padding: 5px 10px;
            border-radius: 15px;
            margin-right: 5px;
            margin-bottom: 5px;
            font-size: 14px;
        }
        .positive-tag {
            background-color: #1e4620;
            color: #4caf50;
        }
        .negative-tag {
            background-color: #391c1c;
            color: #f44336;
        }
        .neutral-tag {
            background-color: #332d15;
            color: #ffeb3b;
        }
        .stTabs [data-baseweb="tab-list"] {
            background-color: #1e1e1e;
            border-radius: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            color: #e0e0e0;
        }
        .stTabs [aria-selected="true"] {
            background-color: #333333;
        }
        .stTextInput > div > div > input {
            background-color: #333333;
            color: #e0e0e0;
        }
        .stTextArea > div > div > textarea {
            background-color: #333333;
            color: #e0e0e0;
        }
        .css-1n543e5 {
            background-color: #1e293b;
            color: #e0e0e0;
        }
        .uploadedFile {
            background-color: #333333 !important;
        }
        .css-16huue1 {
            color: #e0e0e0 !important;
        }
    </style>
    """
