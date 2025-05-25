#!/usr/bin/env python
import sys
import os
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from pathlib import Path
from dotenv import load_dotenv
from db_manager import DatabaseManager
from pubmed_fetcher import search_pubmed, fetch_summaries
from mesh_expander import expand_with_mesh
from transformers import AutoModel, AutoTokenizer
from keybert import KeyBERT

# Load environment variables and connect to the database
ENV_PATH = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)
DB_HOST     = os.getenv("DATABASE_HOST")
DB_PORT     = os.getenv("DATABASE_PORT")
DB_NAME     = os.getenv("DATABASE_NAME")
DB_USER     = os.getenv("DATABASE_USERNAME")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD")

def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller --onefile bundles."""
    base_path = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
    return os.path.join(base_path, relative_path)

class PrimeTimeApp:
    def __init__(self, root):
        pubmedbert_model = AutoModel.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")
        pubmedbert_tokenizer = AutoTokenizer.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")
        self.keyword_extractor = KeyBERT(model=pubmedbert_model)

        self.root = root
        self.root.title("Prime Time Medical Research Opportunities")
        self.root.geometry("1350x750")
        
        # Database manager
        self.db = DatabaseManager()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Database connection frame
        self.db_frame = ttk.LabelFrame(self.main_frame, text="Database Configuration", padding="10")
        self.db_frame.pack(fill=tk.X, pady=10)
        
        # Add database configuration fields
        self.create_db_config_widgets()
        
        # Search frame
        self.search_frame = ttk.LabelFrame(self.main_frame, text="Search PubMed", padding="10")
        self.search_frame.pack(fill=tk.X, pady=10)
        
        # Add search widgets
        self.create_search_widgets()        
        
        # Add results widgets
        self.create_results_widgets()
        
        # Opportunity Analysis frame
        self.opportunity_frame = ttk.LabelFrame(self.main_frame, text="Research Opportunity Analysis", padding="10")
        self.opportunity_frame.pack(fill=tk.X, pady=10)
        
        # Add opportunity analysis widgets
        self.create_opportunity_widgets()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Not connected to database")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initialize app
        self.initialize_app()
    
    def create_db_config_widgets(self):
        form_frame = ttk.Frame(self.db_frame)
        form_frame.pack(fill=tk.X, pady=5)

        ttk.Label(form_frame, text="Host:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.host_var = tk.StringVar(value=DB_HOST)
        ttk.Entry(form_frame, textvariable=self.host_var, width=15).grid(row=0, column=1, padx=2)

        ttk.Label(form_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.port_var = tk.StringVar(value=DB_PORT)
        ttk.Entry(form_frame, textvariable=self.port_var, width=6).grid(row=0, column=3, padx=2)

        ttk.Label(form_frame, text="Database:").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.dbname_var = tk.StringVar(value=DB_NAME)
        ttk.Entry(form_frame, textvariable=self.dbname_var, width=15).grid(row=0, column=5, padx=2)

        ttk.Label(form_frame, text="Username:").grid(row=0, column=6, sticky=tk.W, padx=5)
        self.user_var = tk.StringVar(value=DB_USER)
        ttk.Entry(form_frame, textvariable=self.user_var, width=15).grid(row=0, column=7, padx=2)

        ttk.Label(form_frame, text="Password:").grid(row=0, column=8, sticky=tk.W, padx=5)
        self.password_var = tk.StringVar(value=DB_PASSWORD)
        ttk.Entry(form_frame, textvariable=self.password_var, show="*", width=15).grid(row=0, column=9, padx=2)

        self.connect_btn = ttk.Button(form_frame, text="Connect", command=self.connect_to_db)
        self.connect_btn.grid(row=0, column=11, padx=5)

    def create_search_widgets(self):
        self.search_container = ttk.Frame(self.search_frame)
        self.search_container.pack(fill=tk.BOTH, expand=True)

        self.left_right_frame = ttk.Frame(self.search_container)
        self.left_right_frame.pack(fill=tk.BOTH, expand=True)

        self.left_frame = ttk.Frame(self.left_right_frame, width=400)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        ttk.Label(self.left_frame, text="Type in your research idea:").pack(anchor=tk.W, padx=5, pady=(5, 0))
        self.idea_text = tk.Text(self.left_frame, height=6, width=50, wrap=tk.WORD)
        self.idea_text.pack(padx=5, pady=5)

        self.generate_btn = ttk.Button(self.left_frame, text="Generate", command=self.generate_keywords)
        self.generate_btn.pack(padx=5, pady=5)

        ttk.Label(self.left_frame, text="Keywords:").pack(anchor=tk.W, padx=5, pady=(10, 0))
        self.keywords_text = tk.Text(self.left_frame, height=6, width=50, wrap=tk.WORD)
        self.keywords_text.pack(padx=5, pady=5)

        self.search_btn = ttk.Button(self.left_frame, text="Search PubMed", command=self.search_pubmed)
        self.search_btn.pack(padx=5, pady=(10, 0))
        self.search_btn.config(state=tk.DISABLED)

        self.results_frame = ttk.LabelFrame(self.left_right_frame, text="Articles in Database", padding="10")
        self.results_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        date_frame = ttk.Frame(self.search_frame)
        date_frame.pack(fill=tk.X, pady=5)

        ttk.Label(date_frame, text="Start Date (YYYY-MM-DD):").pack(side=tk.LEFT, padx=5)
        self.start_date_var = tk.StringVar()
        ttk.Entry(date_frame, textvariable=self.start_date_var, width=12).pack(side=tk.LEFT)

        ttk.Label(date_frame, text="End Date (YYYY-MM-DD):").pack(side=tk.LEFT, padx=5)
        self.end_date_var = tk.StringVar()
        ttk.Entry(date_frame, textvariable=self.end_date_var, width=12).pack(side=tk.LEFT)

        ttk.Label(date_frame, text="Max Results:").pack(side=tk.LEFT, padx=10)
        self.max_results_var = tk.StringVar(value="1000")
        ttk.Spinbox(date_frame, from_=1, to=50, textvariable=self.max_results_var, width=5).pack(side=tk.LEFT)

    def create_results_widgets(self):
        # Create a frame for the table
        table_frame = ttk.Frame(self.results_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create treeview
        columns = ("PMID", "Title", "Journal", "Publication Date", "Authors", "Citations")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # Set column headings
        for col in columns:
            self.tree.heading(col, text=col)
            width = 100 if col != "Title" else 300
            self.tree.column(col, width=width)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Pack scrollbars and treeview
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind double-click event
        self.tree.bind("<Double-1>", self.show_article_details)
        
        refresh_frame = ttk.Frame(self.results_frame)
        refresh_frame.pack(fill=tk.X, pady=5)

        # Export CSV button
        self.export_btn = ttk.Button(refresh_frame, text="Export CSV", command=self.export_to_csv)
        self.export_btn.pack(side=tk.RIGHT, padx=5)

        self.refresh_btn = ttk.Button(refresh_frame, text="Refresh Articles", command=self.refresh_articles)
        self.refresh_btn.pack(side=tk.RIGHT, padx=5)
        self.refresh_btn.config(state=tk.DISABLED)

    
    def create_opportunity_widgets(self):
        metrics_frame = ttk.Frame(self.opportunity_frame)
        metrics_frame.pack(fill=tk.X, pady=5)
        
        # Metrics display
        self.publication_count_var = tk.StringVar(value="Publications: 0")
        ttk.Label(metrics_frame, textvariable=self.publication_count_var).pack(side=tk.LEFT, padx=20)
        
        self.total_citations_var = tk.StringVar(value="Total Citations: 0")
        ttk.Label(metrics_frame, textvariable=self.total_citations_var).pack(side=tk.LEFT, padx=20)
        
        self.avg_citations_var = tk.StringVar(value="Avg Citations: 0")
        ttk.Label(metrics_frame, textvariable=self.avg_citations_var).pack(side=tk.LEFT, padx=20)
        
        score_frame = ttk.Frame(self.opportunity_frame)
        score_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(score_frame, text="Opportunity Score:", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=20)
        
        self.score_var = tk.StringVar(value="0.0")
        ttk.Label(score_frame, textvariable=self.score_var, font=("Arial", 14, "bold")).pack(side=tk.LEFT, padx=5)
        
        self.recommendation_var = tk.StringVar(value="No data available")
        ttk.Label(score_frame, textvariable=self.recommendation_var, font=("Arial", 12)).pack(side=tk.RIGHT, padx=20)
    
    def initialize_app(self):
        """Initialize application state"""
        # Try to connect with default settings
        self.connect_to_db()
    
    def connect_to_db(self):
        """Connect to the PostgreSQL database"""
        try:
            # Close existing connection if any
            if hasattr(self, 'db') and self.db:
                self.db.close()
            
            # Create new connection
            self.db = DatabaseManager(
                dbname=self.dbname_var.get(),
                user=self.user_var.get(),
                password=self.password_var.get(),
                host=self.host_var.get(),
                port=self.port_var.get()
            )
            
            if self.db.connect():
                self.status_var.set(f"Connected to database {self.dbname_var.get()}")
                self.refresh_btn.config(state=tk.NORMAL)
                self.search_btn.config(state=tk.NORMAL)
                self.refresh_articles()
            else:
                messagebox.showerror("Connection Error", "Failed to connect to database.")
                self.status_var.set("Database connection failed")
        except Exception as e:
            messagebox.showerror("Connection Error", f"An error occurred: {e}")
            self.status_var.set("Database connection error")
    
    def initialize_db(self):
        """Initialize database schema"""
        try:
            if self.db.initialize_database():
                messagebox.showinfo("Success", "Database initialized successfully.")
                self.status_var.set("Database initialized")
                self.refresh_articles()
            else:
                messagebox.showerror("Error", "Failed to initialize database.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
    
    def search_pubmed(self):
        raw_keywords = self.keywords_text.get("1.0", tk.END).strip().replace("\n", " ")
        keyword_list = [kw.strip() for kw in raw_keywords.split(";") if kw.strip()]
        query_groups = []

        for kw in keyword_list:
            expanded = expand_with_mesh(kw)
            if expanded:
                group = "(" + " OR ".join(expanded) + ")"
                query_groups.append(group)

        query = " AND ".join(query_groups)

        if not query:
            messagebox.showwarning("Warning", "Please enter a search term.")
            return
        
        try:
            max_results = int(self.max_results_var.get())
        except ValueError:
            max_results = 10
        
        def search_task():
            try:
                self.status_var.set(f"Searching PubMed for '{query}'...")
                self.search_btn.config(state=tk.DISABLED)
                
                start_date = self.start_date_var.get().strip() or None
                end_date = self.end_date_var.get().strip() or None
                
                pmids = search_pubmed(query, max_results, start_date=start_date, end_date=end_date)
                if not pmids:
                    self.root.after(0, lambda: messagebox.showinfo("Search Results", "No results found."))
                    self.root.after(0, lambda: self.status_var.set("No results found"))
                    self.root.after(0, lambda: self.search_btn.config(state=tk.NORMAL))
                    return
                
                self.status_var.set(f"Found {len(pmids)} articles. Fetching details...")
                
                # Fetch article details
                articles = fetch_summaries(pmids)
                
                # Store articles in database
                count = 0
                for article in articles:
                    if not self.db.article_exists(article["PMID"]):
                        article_id = self.db.insert_article(article)
                        if article_id:
                            count += 1
                
                # Update UI
                self.root.after(0, lambda: self.status_var.set(f"Added {count} new articles to database"))
                self.root.after(0, lambda: self.refresh_articles())
                self.root.after(0, lambda: messagebox.showinfo("Search Results", f"Added {count} new articles to database"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {e}"))
                self.root.after(0, lambda: self.status_var.set("Search error"))
            finally:
                self.root.after(0, lambda: self.search_btn.config(state=tk.NORMAL))
        
        # Run search in a separate thread
        threading.Thread(target=search_task, daemon=True).start()
    
    def generate_keywords(self):
        idea = self.idea_text.get("1.0", tk.END).strip()
        if not idea:
            messagebox.showwarning("Warning", "Please enter your research idea first.")
            return

        try:
            # Extract keywords using MMR (diverse and relevant)
            keywords = self.keyword_extractor.extract_keywords(
                idea,
                keyphrase_ngram_range=(1, 4),
                stop_words='english',
                use_mmr=True,
                diversity=0.7,
                nr_candidates=100,
                top_n=10
            )

            # Filter: keep those with score ≥ threshold
            keywords = [(phrase, score) for phrase, score in keywords if score >= 0.5]

            # Display results
            self.keywords_text.delete("1.0", tk.END)
            self.keywords_text.insert(tk.END, "; ".join([kw[0] for kw in keywords]))

        except Exception as e:
            messagebox.showerror("Error", f"Keyword extraction failed: {e}")

    def export_to_csv(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"prime_time_export_{timestamp}.csv"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile=default_name,
            title="Export Articles to CSV"
        )
        if not file_path:
            return  # User cancelled

        success = self.db.export_to_csv(file_path)
        if success:
            messagebox.showinfo("Export Complete", f"Articles exported to:\n{file_path}")
        else:
            messagebox.showerror("Error", "Failed to export articles to CSV.")
    
    def refresh_articles(self):
        """Refresh articles displayed in the treeview"""
        try:
            # Clear existing data
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Get all articles from database
            articles = self.db.get_all_articles()
            
            # Populate treeview
            for article in articles:
                authors = ", ".join(article["authors"]) if article["authors"] and article["authors"][0] else ""
                pub_date = article["pub_date"].strftime("%Y-%m-%d") if article["pub_date"] else ""
                
                self.tree.insert("", tk.END, values=(
                    article["pmid"],
                    article["title"],
                    article["journal"],
                    pub_date,
                    authors[:50] + "..." if len(authors) > 50 else authors,
                    article["citation_count"]
                ))
            
            self.status_var.set(f"Displaying {len(articles)} articles")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.status_var.set("Error refreshing articles")
    
    def show_article_details(self, event):
        """Show detailed information about a selected article"""
        try:
            item = self.tree.selection()[0]
            pmid = self.tree.item(item, "values")[0]
            
            article = self.db.get_article_by_pmid(pmid)
            if not article:
                messagebox.showerror("Error", "Article not found in database.")
                return
            
            # Create detail window
            detail_window = tk.Toplevel(self.root)
            detail_window.title(f"Article Details - {pmid}")
            detail_window.geometry("800x600")
            
            # Add details
            main_frame = ttk.Frame(detail_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            title_label = ttk.Label(main_frame, text=article["title"], font=("Arial", 12, "bold"), wraplength=780)
            title_label.pack(fill=tk.X, pady=5)
            
            # Journal and date
            pub_info = f"{article['journal']} - {article['pub_date'].strftime('%Y-%m-%d') if article['pub_date'] else 'N/A'}"
            ttk.Label(main_frame, text=pub_info).pack(fill=tk.X, pady=2)
            
            # Authors
            authors = ", ".join(article["authors"]) if article["authors"] and article["authors"][0] else "Unknown"
            ttk.Label(main_frame, text=f"Authors: {authors}", wraplength=780).pack(fill=tk.X, pady=2)
            
            # PMID & DOI
            identifiers = f"PMID: {article['pmid']} | DOI: {article['doi'] if article['doi'] else 'N/A'}"
            ttk.Label(main_frame, text=identifiers).pack(fill=tk.X, pady=2)
            
            # Citations
            ttk.Label(main_frame, text=f"Citations: {article['citation_count'] or 0}").pack(fill=tk.X, pady=2)
            
            # Abstract
            ttk.Label(main_frame, text="Abstract:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 0))
            abstract_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=15)
            abstract_text.pack(fill=tk.BOTH, expand=True, pady=5)
            abstract_text.insert(tk.END, article["abstract"] if article["abstract"] else "No abstract available")
            abstract_text.config(state=tk.DISABLED)
            
            # Close button
            ttk.Button(main_frame, text="Close", command=detail_window.destroy).pack(pady=10)
        except IndexError:
            messagebox.showwarning("Warning", "Please select an article first.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

def main():
    """Main application function"""
    root = tk.Tk()
    app = PrimeTimeApp(root)
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print("🔥 Unhandled exception:", e, file=sys.stderr)
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)