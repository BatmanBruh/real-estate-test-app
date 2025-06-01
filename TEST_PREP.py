import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import time
import re
import json
import os
from typing import Dict, List, Optional


class RealEstateTestApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Real Estate Licensing Practice Test")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c3e50')

        # Test data and state
        self.all_questions = []
        self.current_questions = []
        self.user_answers = {}
        self.current_question_index = 0
        self.wrong_questions = []
        self.correct_count = 0
        self.total_answered = 0
        self.is_mini_test = False
        self.start_time = None
        self.test_file_loaded = False

        # Flash cards state
        self.flash_cards_mode = False
        self.is_mini_flash_cards = False
        self.current_flash_cards = []
        self.current_flash_index = 0
        self.answer_revealed = False

        # Persistence file paths
        self.test_data_file = "saved_test_data.json"
        self.progress_file = "saved_progress.json"

        # Load saved data first
        self.load_saved_data()

        # Load default questions if no saved test data (sample)
        if not self.all_questions:
            self.load_default_questions()

        # Create main menu first
        self.create_main_menu()

    def load_default_questions(self):
        """Load default sample questions"""
        self.all_questions = [
            {
                'number': 1,
                'question': 'Which of the following statements is correct in relation to deed and zoning restrictions?',
                'options': {
                    'a': 'Zoning regulations are imposed by the Federal government',
                    'b': 'Deed restrictions are imposed by individuals',
                    'c': 'If there\'s a conflict between a deed restriction and zoning regulation, the deed restrictions will apply',
                    'd': 'None of the above'
                },
                'correct_answer': 'b',
                'feedback': 'Both restrictive covenants and zoning impose restrictions on private property uses. However, zoning is established/enforced by local governments and is based on law and restrictive covenants arise from contractual agreements.'
            },
            {
                'number': 2,
                'question': 'Which of the following amounts is prorated between buyer and seller at closing?',
                'options': {
                    'a': 'HOA fees',
                    'b': 'Title Insurance payment',
                    'c': 'Recording fees',
                    'd': 'Commission'
                },
                'correct_answer': 'a',
                'feedback': 'Recording fees (seller), commission (both parties pay separately) and title insurance (buyers) are NOT prorated. HOA fees, utilities and property taxes are typically prorated.'
            },
            {
                'number': 3,
                'question': 'Under the Equal Credit Opportunity Act (ECOA), which of the following would constitute prohibited discrimination?',
                'options': {
                    'a': 'Denying a mortgage because the applicant receives public assistance',
                    'b': 'Refusing to lend to applicants who don\'t meet income requirements',
                    'c': 'Denying credit to an applicant due to poor credit history',
                    'd': 'Requiring additional documentation for applicants employed in their current position less than 2 years'
                },
                'correct_answer': 'a',
                'feedback': 'The ECOA prohibits discrimination based on protected characteristics, including the receipt of public assistance.'
            },
            {
                'number': 4,
                'question': 'Stan is a broker who represents both the buyer and seller in a real estate transaction. To avoid conflicts, Stan appoints Agent A to represent the seller and Agent B to represent the buyer. Both agents work under Stan\'s brokerage. What type of agency relationship is this?',
                'options': {
                    'a': 'Dual agency',
                    'b': 'Transactional agency',
                    'c': 'Exclusive buyer agency',
                    'd': 'Designated agency'
                },
                'correct_answer': 'd',
                'feedback': 'In a designated agency, the broker represents both parties in the transaction but appoints separate agents to represent each client.'
            },
            {
                'number': 5,
                'question': 'Which of the following firm names is in compliance with board regulations?',
                'options': {
                    'a': 'Zen Realty',
                    'b': 'Salesperson Sally Homes',
                    'c': 'Broker Bill Realty',
                    'd': 'Either A or C'
                },
                'correct_answer': 'd',
                'feedback': 'All firms may operate under fictitious names. However, non-broker owned firms can only be licensed in the company\'s legal name. The name of a salesperson cannot appear in the firm name.'
            }
        ]

    def save_test_data(self):
        """Save current test data to file"""
        try:
            data = {
                'questions': self.all_questions,
                'test_file_loaded': self.test_file_loaded,
                'timestamp': time.time()
            }
            with open(self.test_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"DEBUG: Saved {len(self.all_questions)} questions to {self.test_data_file}")
        except Exception as e:
            print(f"DEBUG: Error saving test data: {e}")

    def save_progress_data(self):
        """Save current progress (wrong questions) to file"""
        try:
            data = {
                'wrong_questions': self.wrong_questions,
                'timestamp': time.time()
            }
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"DEBUG: Saved {len(self.wrong_questions)} wrong questions to {self.progress_file}")
        except Exception as e:
            print(f"DEBUG: Error saving progress data: {e}")

    def load_saved_data(self):
        """Load saved test data and progress on startup"""
        # Load test data
        try:
            if os.path.exists(self.test_data_file):
                with open(self.test_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.all_questions = data.get('questions', [])
                    self.test_file_loaded = data.get('test_file_loaded', False)
                    print(f"DEBUG: Loaded {len(self.all_questions)} questions from saved file")
            else:
                print("DEBUG: No saved test data found")
        except Exception as e:
            print(f"DEBUG: Error loading test data: {e}")
            self.all_questions = []
            self.test_file_loaded = False

        # Load progress data
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.wrong_questions = data.get('wrong_questions', [])
                    print(f"DEBUG: Loaded {len(self.wrong_questions)} wrong questions from saved file")
            else:
                print("DEBUG: No saved progress data found")
        except Exception as e:
            print(f"DEBUG: Error loading progress data: {e}")
            self.wrong_questions = []

    def parse_test_file(self, file_content):
        """Parse uploaded test file and extract questions"""
        questions = []

        try:
            # Split by question markers
            question_blocks = re.split(r'\*\*Question (\d+)\*\*', file_content)

            # Process each question (skip first empty element)
            for i in range(1, len(question_blocks), 2):
                if i + 1 < len(question_blocks):
                    question_num = int(question_blocks[i])
                    content = question_blocks[i + 1]

                    # Extract question text
                    question_match = re.search(r'\*\*Question text\*\*(.*?)Question \d+Answer', content, re.DOTALL)
                    if not question_match:
                        continue

                    question_text = question_match.group(1).strip()
                    question_text = re.sub(r'\s+', ' ', question_text)  # Clean whitespace

                    # Extract multiple choice options
                    options = {}

                    # Look for answer section
                    answer_section = re.search(r'Question \d+Answer(.*?)\*\*Feedback\*\*', content, re.DOTALL)
                    if answer_section:
                        answer_text = answer_section.group(1)

                        # Extract options using regex
                        option_pattern = r'([a-d])\\?\.\s*(.*?)(?=\n[a-d]\\?\.|$)'
                        option_matches = re.findall(option_pattern, answer_text, re.DOTALL)

                        for opt_letter, opt_text in option_matches:
                            # Clean up option text
                            opt_text = re.sub(r'\s+', ' ', opt_text.strip())
                            opt_text = opt_text.replace('\\', '')
                            if opt_text and not opt_text.startswith('**'):
                                options[opt_letter] = opt_text

                    # Extract correct answer
                    answer_match = re.search(r'The correct answer is:\s*(.+)', content)
                    if answer_match:
                        correct_answer_text = answer_match.group(1).strip()

                        # Try to match correct answer to option letter
                        correct_letter = None
                        for letter, option_text in options.items():
                            if (option_text.lower() in correct_answer_text.lower() or
                                    correct_answer_text.lower().startswith(option_text.lower()[:30])):
                                correct_letter = letter
                                break

                        # If no match found, try to extract letter from beginning
                        if not correct_letter:
                            letter_match = re.match(r'^([a-d])', correct_answer_text.lower())
                            if letter_match:
                                correct_letter = letter_match.group(1)

                        correct_answer = correct_letter if correct_letter else correct_answer_text
                    else:
                        correct_answer = ""

                    # Extract feedback
                    feedback_match = re.search(r'\*\*Feedback\*\*(.*?)The correct answer is:', content, re.DOTALL)
                    feedback = ""
                    if feedback_match:
                        feedback = re.sub(r'\s+', ' ', feedback_match.group(1).strip())

                    # Only add question if it has valid options
                    if len(options) >= 2 and correct_answer:
                        questions.append({
                            'number': question_num,
                            'question': question_text,
                            'options': options,
                            'correct_answer': correct_answer,
                            'feedback': feedback
                        })

            return questions

        except Exception as e:
            messagebox.showerror("Parsing Error", f"Error parsing test file: {str(e)}")
            return []

    def upload_test_file(self):
        """Allow user to upload a test file"""
        file_path = filedialog.askopenfilename(
            title="Select Test File",
            filetypes=[
                ("Text files", "*.txt"),
                ("Word documents", "*.docx"),
                ("All files", "*.*")
            ]
        )

        if not file_path:
            return

        try:
            # Read file content
            if file_path.endswith('.docx'):
                # Handle Word documents
                try:
                    import docx
                    doc = docx.Document(file_path)
                    content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                except ImportError:
                    messagebox.showerror("Error",
                                         "Please install python-docx to read Word documents:\npip install python-docx")
                    return
            else:
                # Handle text files
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()

            # Parse the content
            questions = self.parse_test_file(content)

            if questions:
                self.all_questions = questions
                self.test_file_loaded = True
                self.save_test_data()  # Save the uploaded test data
                messagebox.showinfo("Success",
                                    f"✅ Successfully loaded {len(questions)} questions from file!\n\n"
                                    f"File: {file_path.split('/')[-1]}\n\n"
                                    f"📁 Test data saved - no need to re-upload!")
                self.create_main_menu()  # Refresh menu to show loaded test
            else:
                messagebox.showerror("Error",
                                     "❌ No valid questions found in the file.\n\n"
                                     "Please make sure the file contains questions in the correct format.")

        except Exception as e:
            messagebox.showerror("Error", f"❌ Error reading file: {str(e)}")

    def create_main_menu(self):
        """Create the main menu interface with scrolling capability"""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create main canvas and scrollbar for scrolling
        canvas = tk.Canvas(self.root, bg='#2c3e50')
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#2c3e50')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mousewheel to canvas for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)

        # Use scrollable_frame as main_container
        main_container = scrollable_frame

        # Title section
        title_frame = tk.Frame(main_container, bg='#2c3e50')
        title_frame.pack(pady=40)

        title_label = tk.Label(title_frame,
                               text="🏠 REAL ESTATE LICENSING PRACTICE TEST",
                               font=('Arial', 24, 'bold'),
                               fg='#ecf0f1',
                               bg='#2c3e50')
        title_label.pack()

        subtitle_label = tk.Label(title_frame,
                                  text="Master Your Real Estate Knowledge",
                                  font=('Arial', 14),
                                  fg='#bdc3c7',
                                  bg='#2c3e50')
        subtitle_label.pack(pady=10)

        # File status indicator
        status_text = f"📁 Loaded: {len(self.all_questions)} questions"
        if self.test_file_loaded:
            status_text += " (Saved Custom File) ✅"
        else:
            status_text += " (Sample Questions) ⚠️"

        # Add progress status if wrong questions exist
        if self.wrong_questions:
            status_text += f"\n📚 Study Available: {len(self.wrong_questions)} wrong questions from previous test"

        status_label = tk.Label(title_frame,
                                text=status_text,
                                font=('Arial', 11),
                                fg='#f39c12',
                                bg='#2c3e50')
        status_label.pack(pady=5)

        # Upload section
        upload_frame = tk.Frame(main_container, bg='#8e44ad', relief=tk.RAISED, bd=2)
        upload_frame.pack(pady=20, padx=100, fill=tk.X)

        upload_title = tk.Label(upload_frame,
                                text="📤 UPLOAD YOUR TEST FILE",
                                font=('Arial', 16, 'bold'),
                                fg='#ecf0f1',
                                bg='#8e44ad')
        upload_title.pack(pady=15)

        upload_text = """
Upload your own test file with multiple choice questions for the complete exam experience!
📝 REQUIREMENTS: Questions must have A, B, C, D answer options
📊 FLEXIBLE: Works with any number of questions (50, 120, 200+ all supported!)
📁 FORMATS: Supported formats: .txt, .docx
📋 FORMAT: Questions should contain Question numbers, multiple choice options, correct answers, and feedback.

💾 Your test file will be automatically saved - no need to re-upload each session!
"""

        upload_label = tk.Label(upload_frame,
                                text=upload_text,
                                font=('Arial', 11),
                                fg='#ecf0f1',
                                bg='#8e44ad',
                                justify=tk.CENTER)
        upload_label.pack(pady=(0, 10), padx=20)

        upload_button = tk.Button(upload_frame,
                                  text="📤 UPLOAD TEST FILE",
                                  font=('Arial', 12, 'bold'),
                                  bg='#9b59b6',
                                  fg='white',
                                  activebackground='#8e44ad',
                                  activeforeground='white',
                                  padx=20,
                                  pady=10,
                                  cursor='hand2',
                                  command=self.upload_test_file)
        upload_button.pack(pady=(0, 15))

        # Instructions section
        instructions_frame = tk.Frame(main_container, bg='#34495e', relief=tk.RAISED, bd=2)
        instructions_frame.pack(pady=20, padx=100, fill=tk.X)

        instructions_title = tk.Label(instructions_frame,
                                      text="📋 HOW TO USE THIS APPLICATION",
                                      font=('Arial', 16, 'bold'),
                                      fg='#ecf0f1',
                                      bg='#34495e')
        instructions_title.pack(pady=15)

        instructions_text = """
🎯 MAIN TEST FEATURES:
• Take the full practice test with all available questions
• MULTIPLE CHOICE ONLY: Designed for A, B, C, D format questions
• Real-time scoring shows you immediately if your answer is correct or incorrect
• Navigate between questions using Previous/Next buttons
• Submit test at any time - unanswered questions are allowed
• View detailed explanations for each question

📊 SCORING SYSTEM:
• Your current score is displayed in real-time as you answer questions
• 75% or higher is considered PASSING
• Detailed results show which questions you got wrong

🔄 MINI TEST (REVIEW MODE):
• After completing the main test, you can take a "Mini Test"
• Mini Test contains ONLY the questions you answered incorrectly
• Perfect for focusing your study on weak areas

💾 PERSISTENCE FEATURES:
• Your uploaded test file is automatically saved - no need to re-upload!
• Your study progress (wrong questions) is saved between sessions
• Close the program anytime and continue studying later
• Mini Test and Mini Flash Cards remain available after restart

📁 FILE FLEXIBILITY:
• Works with ANY number of questions (50, 120, 200+ all supported!)
• Upload practice tests, chapter quizzes, or full exams
• Automatically adapts to your test size

⏱️ ADDITIONAL FEATURES:
• Timer tracks how long you take
• Progress bar shows completion status
• Jump to any question number
• Upload your own test files

Ready to test your real estate knowledge? Click "START FULL TEST" below!
"""

        instructions_label = tk.Label(instructions_frame,
                                      text=instructions_text,
                                      font=('Arial', 11),
                                      fg='#ecf0f1',
                                      bg='#34495e',
                                      justify=tk.LEFT)
        instructions_label.pack(pady=20, padx=30)

        # Buttons section
        buttons_frame = tk.Frame(main_container, bg='#2c3e50')
        buttons_frame.pack(pady=30)

        # Start test button
        start_button = tk.Button(buttons_frame,
                                 text=f"🚀 START FULL TEST ({len(self.all_questions)} Questions)",
                                 font=('Arial', 16, 'bold'),
                                 bg='#27ae60',
                                 fg='white',
                                 activebackground='#2ecc71',
                                 activeforeground='white',
                                 padx=30,
                                 pady=15,
                                 cursor='hand2',
                                 command=self.start_full_test)
        start_button.pack(pady=10)

        # Flash cards button
        flash_cards_button = tk.Button(buttons_frame,
                                       text=f"📚 FLASH CARDS ({len(self.all_questions)} Questions)",
                                       font=('Arial', 14, 'bold'),
                                       bg='#9b59b6',
                                       fg='white',
                                       activebackground='#8e44ad',
                                       activeforeground='white',
                                       padx=25,
                                       pady=12,
                                       cursor='hand2',
                                       command=self.start_flash_cards)
        flash_cards_button.pack(pady=5)

        # Mini test button (if wrong questions exist from previous test)
        if self.wrong_questions:
            mini_test_button = tk.Button(buttons_frame,
                                         text=f"🔄 TAKE MINI TEST ({len(self.wrong_questions)} Questions)",
                                         font=('Arial', 14, 'bold'),
                                         bg='#e74c3c',
                                         fg='white',
                                         activebackground='#c0392b',
                                         activeforeground='white',
                                         padx=25,
                                         pady=12,
                                         cursor='hand2',
                                         command=self.start_mini_test)
            mini_test_button.pack(pady=5)

            # Mini flash cards button (if wrong questions exist)
            mini_flash_button = tk.Button(buttons_frame,
                                          text=f"📚 MINI FLASH CARDS ({len(self.wrong_questions)} Questions)",
                                          font=('Arial', 14, 'bold'),
                                          bg='#8e44ad',
                                          fg='white',
                                          activebackground='#7d3c98',
                                          activeforeground='white',
                                          padx=25,
                                          pady=12,
                                          cursor='hand2',
                                          command=self.start_mini_flash_cards)
            mini_flash_button.pack(pady=5)

        # Sample test button (only if using sample questions)
        if not self.test_file_loaded:
            sample_button = tk.Button(buttons_frame,
                                      text="📝 SAMPLE TEST (5 Questions)",
                                      font=('Arial', 14),
                                      bg='#3498db',
                                      fg='white',
                                      activebackground='#5dade2',
                                      activeforeground='white',
                                      padx=20,
                                      pady=10,
                                      cursor='hand2',
                                      command=self.start_sample_test)
            sample_button.pack(pady=5)

        # Exit button
        exit_button = tk.Button(buttons_frame,
                                text="❌ EXIT APPLICATION",
                                font=('Arial', 12),
                                bg='#e74c3c',
                                fg='white',
                                activebackground='#ec7063',
                                activeforeground='white',
                                padx=20,
                                pady=8,
                                cursor='hand2',
                                command=self.root.quit)
        exit_button.pack(pady=10)

        # Clear saved data button (if any saved data exists)
        if self.test_file_loaded or self.wrong_questions:
            clear_button = tk.Button(buttons_frame,
                                     text="🗑️ CLEAR SAVED DATA",
                                     font=('Arial', 10),
                                     bg='#7f8c8d',
                                     fg='white',
                                     activebackground='#5d6d7e',
                                     activeforeground='white',
                                     padx=15,
                                     pady=6,
                                     cursor='hand2',
                                     command=self.clear_saved_data)
            clear_button.pack(pady=5)

        # Footer
        footer_label = tk.Label(main_container,
                                text="© 2025 Real Estate Practice Test - Good Luck! 🍀",
                                font=('Arial', 10),
                                fg='#7f8c8d',
                                bg='#2c3e50')
        footer_label.pack(side=tk.BOTTOM, pady=20)

    def start_flash_cards(self):
        """Start flash cards mode with all questions"""
        if not self.all_questions:
            messagebox.showerror("No Questions", "Please upload a test file first!")
            return

        import random
        self.current_flash_cards = self.all_questions.copy()
        random.shuffle(self.current_flash_cards)  # Randomize the questions
        self.is_mini_flash_cards = False
        self.flash_cards_mode = True
        self.current_flash_index = 0
        self.answer_revealed = False
        self.create_flash_cards_interface()

    def start_full_test(self):
        """Start the full test with all questions"""
        if not self.all_questions:
            messagebox.showerror("No Questions", "Please upload a test file first!")
            return

        self.current_questions = self.all_questions.copy()
        self.is_mini_test = False
        self.flash_cards_mode = False
        self.reset_test_state()
        self.create_test_interface()

    def start_mini_flash_cards(self):
        """Start mini flash cards with only wrong questions"""
        print("DEBUG: start_mini_flash_cards method called!")  # Debug line

        if not self.wrong_questions:
            messagebox.showinfo("Perfect Score!", "🎉 You got all questions correct! No wrong answers to study.")
            return

        print(f"DEBUG: Starting mini flash cards with {len(self.wrong_questions)} wrong questions")  # Debug line

        import random
        self.current_flash_cards = self.wrong_questions.copy()
        random.shuffle(self.current_flash_cards)  # Randomize the wrong questions

        # Reset all states to ensure clean flash cards mode
        self.is_mini_flash_cards = True
        self.flash_cards_mode = True
        self.is_mini_test = False  # Make sure this is False
        self.current_flash_index = 0
        self.answer_revealed = False

        print(
            f"DEBUG: Flash cards mode set - is_mini_flash_cards: {self.is_mini_flash_cards}, flash_cards_mode: {self.flash_cards_mode}")  # Debug line

        self.create_flash_cards_interface()

    def start_sample_test(self):
        """Start a sample test with available questions"""
        self.current_questions = self.all_questions.copy()
        self.is_mini_test = False
        self.flash_cards_mode = False
        self.reset_test_state()
        self.create_test_interface()

    def start_mini_test(self):
        """Start mini test with only wrong answers - FIXED VERSION"""
        if not self.wrong_questions:
            messagebox.showinfo("Perfect Score!", "🎉 You got all questions correct! No mini test needed.")
            return

        # Create a deep copy of wrong questions for mini test
        self.current_questions = []
        for wrong_q in self.wrong_questions:
            # Make sure we copy the complete question data
            mini_question = {
                'number': wrong_q['number'],
                'question': wrong_q['question'],
                'options': wrong_q['options'].copy(),
                'correct_answer': wrong_q['correct_answer'],
                'feedback': wrong_q['feedback']
            }
            self.current_questions.append(mini_question)

        self.is_mini_test = True
        self.flash_cards_mode = False
        self.reset_test_state()
        self.create_test_interface()

        print(f"DEBUG: Mini test started with {len(self.current_questions)} wrong questions")  # Debug line

    def reset_test_state(self):
        """Reset all test-related state variables"""
        self.user_answers = {}
        self.current_question_index = 0
        self.correct_count = 0
        self.total_answered = 0
        self.start_time = time.time()
        # Clear any existing answer variable if it exists
        if hasattr(self, 'answer_var'):
            self.answer_var.set("")
        # Reset flash cards state
        self.flash_cards_mode = False
        self.is_mini_flash_cards = False
        self.answer_revealed = False

    def create_test_interface(self):
        """Create the test-taking interface"""
        # Clear main menu
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main frame
        main_frame = tk.Frame(self.root, bg='#ecf0f1')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header frame
        header_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # Title
        test_title = "🔄 MINI TEST (Wrong Answers Only)" if self.is_mini_test else "📚 REAL ESTATE PRACTICE TEST"
        title_label = tk.Label(header_frame,
                               text=test_title,
                               font=('Arial', 18, 'bold'),
                               fg='#ecf0f1',
                               bg='#34495e')
        title_label.pack(pady=10)

        # Progress and scoring info
        info_frame = tk.Frame(header_frame, bg='#34495e')
        info_frame.pack(pady=(0, 10))

        self.progress_label = tk.Label(info_frame,
                                       text="Question 1 of " + str(len(self.current_questions)),
                                       font=('Arial', 12),
                                       fg='#bdc3c7',
                                       bg='#34495e')
        self.progress_label.pack()

        # Real-time score display
        self.score_label = tk.Label(info_frame,
                                    text="Score: 0/0 (0.0%) | Status: Not Started",
                                    font=('Arial', 12, 'bold'),
                                    fg='#f39c12',
                                    bg='#34495e')
        self.score_label.pack(pady=5)

        # Progress bar
        self.progress_bar = ttk.Progressbar(info_frame,
                                            length=600,
                                            mode='determinate',
                                            maximum=len(self.current_questions))
        self.progress_bar.pack(pady=5)

        # Timer
        self.timer_label = tk.Label(info_frame,
                                    text="Time: 00:00",
                                    font=('Arial', 11),
                                    fg='#95a5a6',
                                    bg='#34495e')
        self.timer_label.pack()

        # Question frame
        question_frame = tk.LabelFrame(main_frame,
                                       text="Question",
                                       font=('Arial', 12, 'bold'),
                                       bg='#ecf0f1',
                                       fg='#2c3e50')
        question_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.question_text = scrolledtext.ScrolledText(question_frame,
                                                       height=8,
                                                       font=('Arial', 11),
                                                       wrap=tk.WORD,
                                                       state=tk.DISABLED,
                                                       bg='#ffffff')
        self.question_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Options frame
        options_frame = tk.LabelFrame(main_frame,
                                      text="Answer Options",
                                      font=('Arial', 12, 'bold'),
                                      bg='#ecf0f1',
                                      fg='#2c3e50')
        options_frame.pack(fill=tk.X, pady=(0, 10))

        self.answer_var = tk.StringVar()
        self.answer_var.set("")  # Explicitly set to empty string
        self.answer_var.trace('w', self.on_answer_selected)  # Real-time feedback
        self.option_buttons = {}

        for i, letter in enumerate(['a', 'b', 'c', 'd']):
            self.option_buttons[letter] = tk.Radiobutton(options_frame,
                                                         text="",
                                                         variable=self.answer_var,
                                                         value=letter,
                                                         font=('Arial', 11),
                                                         wraplength=800,
                                                         justify=tk.LEFT,
                                                         anchor="w",
                                                         bg='#ecf0f1',
                                                         selectcolor='#3498db',
                                                         activebackground='#d5dbdb',
                                                         indicatoron=True,
                                                         relief=tk.FLAT,
                                                         borderwidth=1)
            self.option_buttons[letter].pack(anchor=tk.W, padx=15, pady=5)

        # Feedback frame for real-time results
        self.feedback_frame = tk.Frame(main_frame, bg='#ecf0f1')
        self.feedback_frame.pack(fill=tk.X, pady=(0, 10))

        self.feedback_label = tk.Label(self.feedback_frame,
                                       text="",
                                       font=('Arial', 12, 'bold'),
                                       bg='#ecf0f1')
        self.feedback_label.pack()

        # Navigation frame
        nav_frame = tk.Frame(main_frame, bg='#ecf0f1')
        nav_frame.pack(fill=tk.X)

        # Left side navigation
        left_nav = tk.Frame(nav_frame, bg='#ecf0f1')
        left_nav.pack(side=tk.LEFT)

        self.prev_button = tk.Button(left_nav,
                                     text="⬅️ Previous",
                                     font=('Arial', 11),
                                     bg='#95a5a6',
                                     fg='white',
                                     padx=15,
                                     pady=8,
                                     command=self.previous_question)
        self.prev_button.pack(side=tk.LEFT, padx=(0, 10))

        self.next_button = tk.Button(left_nav,
                                     text="Next ➡️",
                                     font=('Arial', 11),
                                     bg='#3498db',
                                     fg='white',
                                     padx=15,
                                     pady=8,
                                     command=self.next_question)
        self.next_button.pack(side=tk.LEFT, padx=(0, 10))

        # Center navigation
        center_nav = tk.Frame(nav_frame, bg='#ecf0f1')
        center_nav.pack(side=tk.LEFT, expand=True)

        jump_button = tk.Button(center_nav,
                                text="🔍 Jump to Question",
                                font=('Arial', 10),
                                bg='#f39c12',
                                fg='white',
                                padx=10,
                                pady=6,
                                command=self.jump_to_question)
        jump_button.pack()

        # Right side navigation
        right_nav = tk.Frame(nav_frame, bg='#ecf0f1')
        right_nav.pack(side=tk.RIGHT)

        menu_button = tk.Button(right_nav,
                                text="🏠 Main Menu",
                                font=('Arial', 10),
                                bg='#7f8c8d',
                                fg='white',
                                padx=10,
                                pady=6,
                                command=self.return_to_menu)
        menu_button.pack(side=tk.RIGHT, padx=(10, 0))

        self.submit_button = tk.Button(right_nav,
                                       text="✅ Submit Test",
                                       font=('Arial', 11, 'bold'),
                                       bg='#27ae60',
                                       fg='white',
                                       padx=20,
                                       pady=8,
                                       command=self.submit_test)
        self.submit_button.pack(side=tk.RIGHT, padx=(10, 10))

        # Start timer and display first question
        self.start_timer()
        self.display_question()

    def create_flash_cards_interface(self):
        """Create the flash cards interface"""
        print(
            f"DEBUG: Creating flash cards interface - flash_cards_mode: {self.flash_cards_mode}, is_mini_flash_cards: {self.is_mini_flash_cards}")  # Debug line

        # Safety check to ensure we're in flash cards mode
        if not self.flash_cards_mode:
            print("ERROR: Not in flash cards mode, returning to menu")  # Debug line
            self.return_to_menu()
            return

        # Check if we have flash cards to display
        if not hasattr(self, 'current_flash_cards') or not self.current_flash_cards:
            print("ERROR: No flash cards to display")  # Debug line
            messagebox.showerror("Error", "No flash cards available")
            self.return_to_menu()
            return

        print(f"DEBUG: About to create interface with {len(self.current_flash_cards)} flash cards")  # Debug line

        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main frame with full window
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        header_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        # Title
        title_text = "📚 MINI FLASH CARDS (Wrong Answers)" if self.is_mini_flash_cards else "📚 FLASH CARDS (All Questions)"
        title_label = tk.Label(header_frame,
                               text=title_text,
                               font=('Arial', 20, 'bold'),
                               fg='#ecf0f1',
                               bg='#34495e')
        title_label.pack(pady=15)

        # Progress info
        total_cards = len(self.current_flash_cards)
        current_card = self.current_flash_index + 1
        self.progress_label = tk.Label(header_frame,
                                       text=f"Card {current_card} of {total_cards}",
                                       font=('Arial', 14),
                                       fg='#bdc3c7',
                                       bg='#34495e')
        self.progress_label.pack(pady=5)

        # Question display frame
        question_frame = tk.Frame(main_frame, bg='#ecf0f1', relief=tk.RAISED, bd=3)
        question_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Question text with large font
        self.flash_question_text = scrolledtext.ScrolledText(question_frame,
                                                             font=('Arial', 16, 'bold'),
                                                             wrap=tk.WORD,
                                                             state=tk.DISABLED,
                                                             bg='#ffffff',
                                                             fg='#2c3e50')
        self.flash_question_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Answer display frame (initially hidden)
        self.answer_frame = tk.Frame(main_frame, bg='#e8f5e8', relief=tk.RAISED, bd=3)

        self.flash_answer_text = scrolledtext.ScrolledText(self.answer_frame,
                                                           font=('Arial', 14),
                                                           wrap=tk.WORD,
                                                           state=tk.DISABLED,
                                                           bg='#e8f5e8',
                                                           fg='#27ae60')
        self.flash_answer_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Control buttons frame
        controls_frame = tk.Frame(main_frame, bg='#2c3e50')
        controls_frame.pack(fill=tk.X)

        # Reveal answer button (shown when answer is hidden)
        self.reveal_button = tk.Button(controls_frame,
                                       text="🔍 REVEAL ANSWER",
                                       font=('Arial', 14, 'bold'),
                                       bg='#e74c3c',
                                       fg='white',
                                       padx=30,
                                       pady=12,
                                       command=self.reveal_answer)
        self.reveal_button.pack(pady=10)

        # Navigation buttons frame (shown when answer is revealed)
        self.nav_frame = tk.Frame(controls_frame, bg='#2c3e50')

        # Navigation buttons
        self.prev_flash_button = tk.Button(self.nav_frame,
                                           text="⬅️ PREVIOUS",
                                           font=('Arial', 12, 'bold'),
                                           bg='#95a5a6',
                                           fg='white',
                                           padx=20,
                                           pady=10,
                                           command=self.previous_flash_card)
        self.prev_flash_button.pack(side=tk.LEFT, padx=10)

        self.try_again_button = tk.Button(self.nav_frame,
                                          text="🔄 TRY AGAIN",
                                          font=('Arial', 12, 'bold'),
                                          bg='#f39c12',
                                          fg='white',
                                          padx=20,
                                          pady=10,
                                          command=self.try_again_flash_card)
        self.try_again_button.pack(side=tk.LEFT, padx=10)

        self.next_flash_button = tk.Button(self.nav_frame,
                                           text="NEXT ➡️",
                                           font=('Arial', 12, 'bold'),
                                           bg='#27ae60',
                                           fg='white',
                                           padx=20,
                                           pady=10,
                                           command=self.next_flash_card)
        self.next_flash_button.pack(side=tk.LEFT, padx=10)

        # Mini Test button (only for mini flash cards)
        if self.is_mini_flash_cards:
            mini_test_button = tk.Button(self.nav_frame,
                                         text="🔄 TAKE MINI TEST",
                                         font=('Arial', 12, 'bold'),
                                         bg='#e74c3c',
                                         fg='white',
                                         padx=20,
                                         pady=10,
                                         command=self.start_mini_test)
            mini_test_button.pack(side=tk.RIGHT, padx=10)

        # Main menu button
        menu_button = tk.Button(self.nav_frame,
                                text="🏠 MAIN MENU",
                                font=('Arial', 12),
                                bg='#7f8c8d',
                                fg='white',
                                padx=20,
                                pady=10,
                                command=self.return_to_menu)
        menu_button.pack(side=tk.RIGHT, padx=10)

        # Display the current flash card
        self.display_flash_card()

    def display_flash_card(self):
        """Display the current flash card"""
        if not self.current_flash_cards or self.current_flash_index >= len(self.current_flash_cards):
            self.flash_cards_complete()
            return

        question_data = self.current_flash_cards[self.current_flash_index]

        # Update progress
        total_cards = len(self.current_flash_cards)
        current_card = self.current_flash_index + 1
        self.progress_label.config(text=f"Card {current_card} of {total_cards}")

        # Display question
        self.flash_question_text.config(state=tk.NORMAL)
        self.flash_question_text.delete(1.0, tk.END)
        question_title = f"Question {question_data['number']}:\n\n"
        self.flash_question_text.insert(1.0, question_title + question_data['question'])

        # Highlight question number
        self.flash_question_text.tag_add("title", "1.0", f"1.{len(question_title)}")
        self.flash_question_text.tag_config("title", font=('Arial', 18, 'bold'), foreground='#e74c3c')
        self.flash_question_text.config(state=tk.DISABLED)

        # Show/hide appropriate controls based on answer revealed state
        if self.answer_revealed:
            self.show_answer()
        else:
            self.hide_answer()

    def reveal_answer(self):
        """Reveal the answer and show navigation options"""
        self.answer_revealed = True
        self.show_answer()

    def show_answer(self):
        """Show the answer and navigation buttons"""
        question_data = self.current_flash_cards[self.current_flash_index]

        # Show answer frame
        self.answer_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 20))

        # Display answer and feedback
        self.flash_answer_text.config(state=tk.NORMAL)
        self.flash_answer_text.delete(1.0, tk.END)

        # Find correct answer text
        correct_letter = question_data['correct_answer'].lower()
        correct_option = ""
        if correct_letter in question_data['options']:
            correct_option = question_data['options'][correct_letter]

        answer_text = f"✅ CORRECT ANSWER: {correct_letter.upper()}\n"
        if correct_option:
            answer_text += f"{correct_option}\n\n"
        answer_text += f"💡 EXPLANATION:\n{question_data['feedback']}"

        self.flash_answer_text.insert(1.0, answer_text)
        self.flash_answer_text.config(state=tk.DISABLED)

        # Hide reveal button, show navigation
        self.reveal_button.pack_forget()
        self.nav_frame.pack(pady=10)

        # Update navigation button states
        self.prev_flash_button.config(state=tk.NORMAL if self.current_flash_index > 0 else tk.DISABLED)
        self.next_flash_button.config(
            state=tk.NORMAL if self.current_flash_index < len(self.current_flash_cards) - 1 else tk.DISABLED)

    def hide_answer(self):
        """Hide the answer and show reveal button"""
        # Hide answer frame and navigation
        self.answer_frame.pack_forget()
        self.nav_frame.pack_forget()

        # Show reveal button
        self.reveal_button.pack(pady=10)

    def try_again_flash_card(self):
        """Hide the answer to try again"""
        self.answer_revealed = False
        self.hide_answer()

    def previous_flash_card(self):
        """Go to previous flash card"""
        if self.current_flash_index > 0:
            self.current_flash_index -= 1
            self.answer_revealed = False
            self.display_flash_card()

    def next_flash_card(self):
        """Go to next flash card"""
        if self.current_flash_index < len(self.current_flash_cards) - 1:
            self.current_flash_index += 1
            self.answer_revealed = False
            self.display_flash_card()
        else:
            self.flash_cards_complete()

    def flash_cards_complete(self):
        """Handle completion of flash cards"""
        card_type = "Mini Flash Cards" if self.is_mini_flash_cards else "Flash Cards"
        message = f"🎉 {card_type} Complete!\n\n"
        message += f"You've reviewed {len(self.current_flash_cards)} questions.\n\n"

        if self.is_mini_flash_cards:
            message += "Great job studying your weak areas!\nReady to test yourself or continue studying?"
        else:
            message += "Excellent studying! Ready to take the full test?"

        result = messagebox.showinfo("Flash Cards Complete", message)
        self.return_to_menu()

    def on_answer_selected(self, *args):
        """Handle real-time feedback when user selects an answer"""
        if not self.current_questions or self.current_question_index >= len(self.current_questions):
            return

        selected_answer = self.answer_var.get()
        if not selected_answer:
            return

        current_question = self.current_questions[self.current_question_index]
        correct_answer = current_question['correct_answer']
        question_id = current_question['number']

        # Check if this question was already answered
        was_answered_before = question_id in self.user_answers

        # Save the answer
        self.user_answers[question_id] = selected_answer

        # Provide immediate feedback
        if selected_answer == correct_answer:
            self.feedback_label.config(text="✅ CORRECT! Well done!",
                                       fg='#27ae60')
            if not was_answered_before:
                self.correct_count += 1
        else:
            self.feedback_label.config(text=f"❌ INCORRECT. The correct answer is {correct_answer.upper()}.",
                                       fg='#e74c3c')

        # Update total answered count if this is a new answer
        if not was_answered_before:
            self.total_answered += 1

        # Update real-time score
        self.update_score_display()

    def update_score_display(self):
        """Update the real-time score display"""
        if self.total_answered > 0:
            percentage = (self.correct_count / self.total_answered) * 100
            status = "PASSING" if percentage >= 75 else "NEEDS IMPROVEMENT"
            status_color = '#27ae60' if percentage >= 75 else '#e74c3c'

            score_text = f"Score: {self.correct_count}/{self.total_answered} ({percentage:.1f}%) | Status: {status}"
            self.score_label.config(text=score_text, fg=status_color)
        else:
            self.score_label.config(text="Score: 0/0 (0.0%) | Status: Not Started", fg='#f39c12')

    def start_timer(self):
        """Start and update the timer"""

        def update_timer():
            if hasattr(self, 'start_time') and self.start_time:
                elapsed = int(time.time() - self.start_time)
                minutes = elapsed // 60
                seconds = elapsed % 60
                self.timer_label.config(text=f"Time: {minutes:02d}:{seconds:02d}")
                self.root.after(1000, update_timer)

        update_timer()

    def display_question(self):
        """Display the current question"""
        if not self.current_questions or self.current_question_index >= len(self.current_questions):
            return

        question_data = self.current_questions[self.current_question_index]

        # Update progress
        current_num = self.current_question_index + 1
        total_num = len(self.current_questions)
        self.progress_label.config(text=f"Question {current_num} of {total_num}")
        self.progress_bar.config(value=current_num)

        # Display question text
        self.question_text.config(state=tk.NORMAL)
        self.question_text.delete(1.0, tk.END)
        question_title = f"Question {question_data['number']}: "
        self.question_text.insert(1.0, question_title + question_data['question'])

        # Highlight question number
        self.question_text.tag_add("title", "1.0", f"1.{len(question_title)}")
        self.question_text.tag_config("title", font=('Arial', 11, 'bold'), foreground='#2c3e50')
        self.question_text.config(state=tk.DISABLED)

        # Clear any existing selection first
        self.answer_var.set("")

        # Display options
        for letter, button in self.option_buttons.items():
            if letter in question_data['options']:
                option_text = f"{letter.upper()}. {question_data['options'][letter]}"
                button.config(text=option_text, state=tk.NORMAL)
            else:
                button.config(text="", state=tk.DISABLED)

        # Force update to ensure radio buttons display correctly
        self.root.update_idletasks()

        # Set current answer if exists (after clearing and updating)
        question_id = question_data['number']
        if question_id in self.user_answers:
            self.answer_var.set(self.user_answers[question_id])
            # Show feedback for already answered questions
            self.on_answer_selected()
        else:
            self.feedback_label.config(text="")

        # Update button states
        self.prev_button.config(state=tk.NORMAL if self.current_question_index > 0 else tk.DISABLED)
        self.next_button.config(
            state=tk.NORMAL if self.current_question_index < len(self.current_questions) - 1 else tk.DISABLED)

    def previous_question(self):
        """Go to previous question"""
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.display_question()

    def next_question(self):
        """Go to next question"""
        if self.current_question_index < len(self.current_questions) - 1:
            self.current_question_index += 1
            self.display_question()

    def jump_to_question(self):
        """Jump to a specific question number"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Jump to Question")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Enter question number:", font=('Arial', 12)).pack(pady=20)

        entry = tk.Entry(dialog, font=('Arial', 12), width=10)
        entry.pack(pady=10)
        entry.focus()

        def jump():
            try:
                q_num = int(entry.get())
                if 1 <= q_num <= len(self.current_questions):
                    self.current_question_index = q_num - 1
                    self.display_question()
                    dialog.destroy()
                else:
                    messagebox.showerror("Invalid",
                                         f"Please enter a number between 1 and {len(self.current_questions)}")
            except ValueError:
                messagebox.showerror("Invalid", "Please enter a valid number")

        tk.Button(dialog, text="Jump", command=jump, bg='#3498db', fg='white', padx=20).pack(pady=10)
        entry.bind('<Return>', lambda e: jump())

    def submit_test(self):
        """Submit the test and show results"""
        self.calculate_final_results()

    def calculate_final_results(self):
        """Calculate final test results - FIXED VERSION"""
        # Clear previous wrong questions for fresh calculation
        self.wrong_questions = []
        final_correct = 0

        print(f"DEBUG: Calculating results for {len(self.current_questions)} questions")  # Debug line

        for question in self.current_questions:
            question_id = question['number']
            user_answer = self.user_answers.get(question_id, "")

            print(f"DEBUG: Q{question_id}: User={user_answer}, Correct={question['correct_answer']}")  # Debug line

            if user_answer == question['correct_answer']:
                final_correct += 1
            else:
                # Add to wrong questions - this question was answered incorrectly
                self.wrong_questions.append(question)

        print(f"DEBUG: Final correct: {final_correct}, Wrong questions: {len(self.wrong_questions)}")  # Debug line

        # Save wrong questions for future sessions
        self.save_progress_data()

        total_questions = len(self.current_questions)
        percentage = (final_correct / total_questions) * 100 if total_questions > 0 else 0

        # Calculate time taken
        time_taken = int(time.time() - self.start_time) if self.start_time else 0

        self.show_results(final_correct, total_questions, percentage, time_taken)

    def show_results(self, correct_count: int, total_questions: int, percentage: float, time_taken: int):
        """Display final test results"""
        # Clear test interface
        for widget in self.root.winfo_children():
            widget.destroy()

        # Results container
        results_container = tk.Frame(self.root, bg='#2c3e50')
        results_container.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = tk.Frame(results_container, bg='#34495e', relief=tk.RAISED, bd=3)
        header_frame.pack(fill=tk.X, padx=20, pady=20)

        test_type = "MINI TEST RESULTS" if self.is_mini_test else "FINAL TEST RESULTS"
        header_label = tk.Label(header_frame,
                                text=f"📊 {test_type}",
                                font=('Arial', 20, 'bold'),
                                fg='#ecf0f1',
                                bg='#34495e')
        header_label.pack(pady=15)

        # Score display
        score_frame = tk.Frame(results_container, bg='#2c3e50')
        score_frame.pack(pady=20)

        # Determine grade and color
        if percentage >= 90:
            grade = "A"
            grade_color = "#27ae60"
            status = "EXCELLENT!"
        elif percentage >= 80:
            grade = "B"
            grade_color = "#f39c12"
            status = "GOOD!"
        elif percentage >= 75:
            grade = "C"
            grade_color = "#e67e22"
            status = "PASSING"
        else:
            grade = "F"
            grade_color = "#e74c3c"
            status = "NEEDS IMPROVEMENT"

        # Main score
        score_text = f"{correct_count}/{total_questions} ({percentage:.1f}%)"
        score_label = tk.Label(score_frame,
                               text=score_text,
                               font=('Arial', 24, 'bold'),
                               fg=grade_color,
                               bg='#2c3e50')
        score_label.pack()

        # Grade and status
        grade_label = tk.Label(score_frame,
                               text=f"Grade: {grade} - {status}",
                               font=('Arial', 16, 'bold'),
                               fg=grade_color,
                               bg='#2c3e50')
        grade_label.pack(pady=5)

        # Time
        minutes = time_taken // 60
        seconds = time_taken % 60
        time_label = tk.Label(score_frame,
                              text=f"⏱️ Time: {minutes:02d}:{seconds:02d}",
                              font=('Arial', 12),
                              fg='#bdc3c7',
                              bg='#2c3e50')
        time_label.pack(pady=5)

        # Details frame
        details_frame = tk.LabelFrame(results_container,
                                      text="Detailed Results",
                                      font=('Arial', 14, 'bold'),
                                      bg='#2c3e50',
                                      fg='#ecf0f1')
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        self.results_text = scrolledtext.ScrolledText(details_frame,
                                                      height=15,
                                                      font=('Arial', 10),
                                                      wrap=tk.WORD,
                                                      bg='#ecf0f1')
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Populate results text
        results_content = f"📈 TEST SUMMARY\n"
        results_content += "=" * 50 + "\n\n"
        results_content += f"📝 Test Type: {'Mini Test (Wrong Answers Only)' if self.is_mini_test else 'Full Practice Test'}\n"
        results_content += f"✅ Correct Answers: {correct_count}\n"
        results_content += f"❌ Incorrect Answers: {total_questions - correct_count}\n"
        results_content += f"📊 Percentage: {percentage:.1f}%\n"
        results_content += f"🎯 Grade: {grade}\n"
        results_content += f"⏱️ Time Taken: {minutes:02d}:{seconds:02d}\n\n"

        if self.wrong_questions:
            results_content += f"📚 QUESTIONS TO REVIEW ({len(self.wrong_questions)}):\n"
            results_content += "=" * 50 + "\n\n"

            for i, question in enumerate(self.wrong_questions, 1):
                question_id = question['number']
                user_answer = self.user_answers.get(question_id, "No answer")
                results_content += f"{i}. Question {question_id}:\n"
                results_content += f"   ❓ {question['question'][:150]}{'...' if len(question['question']) > 150 else ''}\n"
                results_content += f"   👤 Your Answer: {user_answer.upper() if user_answer != 'No answer' else user_answer}\n"
                results_content += f"   ✅ Correct Answer: {question['correct_answer'].upper()}\n"
                results_content += f"   💡 Explanation: {question['feedback'][:200]}{'...' if len(question['feedback']) > 200 else ''}\n\n"
        else:
            results_content += "🎉 PERFECT SCORE! You answered all questions correctly!\n"

        self.results_text.insert(1.0, results_content)
        self.results_text.config(state=tk.DISABLED)

        # Buttons frame
        buttons_frame = tk.Frame(results_container, bg='#2c3e50')
        buttons_frame.pack(pady=20)

        # Mini test button (only if there are wrong answers and not already in mini test)
        if self.wrong_questions and not self.is_mini_test:
            mini_test_button = tk.Button(buttons_frame,
                                         text=f"🔄 TAKE MINI TEST ({len(self.wrong_questions)} Questions)",
                                         font=('Arial', 12, 'bold'),
                                         bg='#e74c3c',
                                         fg='white',
                                         padx=20,
                                         pady=10,
                                         command=self.start_mini_test)
            mini_test_button.pack(side=tk.LEFT, padx=10)

            # Mini flash cards button
            mini_flash_button = tk.Button(buttons_frame,
                                          text=f"📚 MINI FLASH CARDS ({len(self.wrong_questions)} Questions)",
                                          font=('Arial', 12, 'bold'),
                                          bg='#9b59b6',
                                          fg='white',
                                          padx=20,
                                          pady=10,
                                          command=self.start_mini_flash_cards)
            mini_flash_button.pack(side=tk.LEFT, padx=10)

        # Restart test button
        restart_text = "🔄 RETAKE MINI TEST" if self.is_mini_test else "🔄 RETAKE FULL TEST"
        restart_button = tk.Button(buttons_frame,
                                   text=restart_text,
                                   font=('Arial', 12),
                                   bg='#3498db',
                                   fg='white',
                                   padx=20,
                                   pady=10,
                                   command=self.restart_current_test)
        restart_button.pack(side=tk.LEFT, padx=10)

        # Main menu button
        menu_button = tk.Button(buttons_frame,
                                text="🏠 MAIN MENU",
                                font=('Arial', 12),
                                bg='#95a5a6',
                                fg='white',
                                padx=20,
                                pady=10,
                                command=self.create_main_menu)
        menu_button.pack(side=tk.LEFT, padx=10)

    def restart_current_test(self):
        """Restart the current test (full or mini)"""
        if self.is_mini_test:
            self.start_mini_test()
        else:
            self.start_full_test()

    def return_to_menu(self):
        """Return to main menu"""
        # Reset all modes
        self.flash_cards_mode = False
        self.is_mini_flash_cards = False
        self.answer_revealed = False
        self.create_main_menu()

    def clear_saved_data(self):
        """Clear all saved data and start fresh"""
        result = messagebox.askyesno("Clear Saved Data",
                                     "⚠️ This will clear all saved data including:\n\n"
                                     "• Your uploaded test file\n"
                                     "• Your study progress (wrong questions)\n\n"
                                     "You'll need to re-upload your test file.\n\n"
                                     "Are you sure you want to continue?")

        if result:
            try:
                # Remove saved files
                if os.path.exists(self.test_data_file):
                    os.remove(self.test_data_file)
                if os.path.exists(self.progress_file):
                    os.remove(self.progress_file)

                # Reset application state
                self.all_questions = []
                self.wrong_questions = []
                self.test_file_loaded = False

                # Load default sample questions
                self.load_default_questions()

                messagebox.showinfo("Data Cleared",
                                    "✅ All saved data has been cleared.\n\n"
                                    "Application reset to default state with sample questions.")

                # Refresh main menu
                self.create_main_menu()

            except Exception as e:
                messagebox.showerror("Error", f"Error clearing saved data: {str(e)}")


def main():
    root = tk.Tk()
    app = RealEstateTestApplication(root)
    root.mainloop()


if __name__ == "__main__":
    main()  
