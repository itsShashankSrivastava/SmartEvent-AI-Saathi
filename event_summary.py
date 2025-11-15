# """
# EventMaster Pro - Professional Event Summary Generator
# Creates comprehensive PDF event planning summaries with budget visualization
# """

# import json
# import os
# import re
# from datetime import datetime
# from typing import Dict, List, Optional, Any, Tuple
# from pathlib import Path
# import base64
# from io import BytesIO
# import requests

# try:
#     import matplotlib.pyplot as plt
#     import matplotlib.patches as patches
#     from reportlab.lib.pagesizes import A4, letter
#     from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
#     from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
#     from reportlab.lib.units import inch, cm
#     from reportlab.lib import colors
#     from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
#     from reportlab.pdfgen import canvas
#     DEPENDENCIES_AVAILABLE = True
# except ImportError:
#     DEPENDENCIES_AVAILABLE = False
#     print("⚠️ PDF generation dependencies not available. Install: pip install matplotlib reportlab")

# class EventSummaryGenerator:
#     def __init__(self):
#         self.output_dir = Path("event_summaries")
#         self.output_dir.mkdir(exist_ok=True)
#         self.llm_url = os.getenv("LLM_URL", "http://localhost:8000/groq/chat/completions")
#         self.llm_token = os.getenv("LLM_TOKEN", "")
        
#         # Dynamic configuration
#         self.event_type_patterns = self._load_event_patterns()
#         self.budget_distributions = self._load_budget_distributions()
#         self.vendor_categories = self._load_vendor_categories()
#         self.color_schemes = self._load_color_schemes()
    
#     def _load_event_patterns(self) -> Dict:
#         """Load event type detection patterns dynamically"""
#         return {
#             "wedding": ["wedding", "marriage", "shaadi", "vivah", "nikah"],
#             "birthday": ["birthday", "bday", "birth", "anniversary"],
#             "corporate": ["corporate", "business", "conference", "meeting", "seminar"],
#             "engagement": ["engagement", "ring", "sagai"],
#             "anniversary": ["anniversary", "celebration"]
#         }
    
#     def _load_budget_distributions(self) -> Dict:
#         """Load budget distribution patterns dynamically"""
#         return {
#             "wedding": {"venue": 35, "catering": 30, "decoration": 15, "photography": 10, "entertainment": 5, "miscellaneous": 5},
#             "birthday": {"venue": 25, "catering": 40, "decoration": 20, "entertainment": 10, "miscellaneous": 5},
#             "corporate": {"venue": 30, "catering": 35, "av_equipment": 15, "materials": 10, "transportation": 5, "miscellaneous": 5},
#             "engagement": {"venue": 30, "catering": 35, "decoration": 20, "photography": 10, "miscellaneous": 5},
#             "anniversary": {"venue": 30, "catering": 35, "decoration": 20, "entertainment": 10, "miscellaneous": 5}
#         }
    
#     def _load_vendor_categories(self) -> Dict:
#         """Load vendor categorization patterns"""
#         return {
#             "catering": ["catering", "food", "kitchen", "chef", "cuisine"],
#             "decoration": ["decoration", "decor", "flower", "styling", "design"],
#             "venue": ["hotel", "venue", "hall", "resort", "palace"],
#             "photography": ["photo", "video", "camera", "shoot", "capture"],
#             "entertainment": ["music", "dj", "band", "dance", "entertainment"],
#             "transportation": ["transport", "car", "bus", "travel"]
#         }
    
#     def _load_color_schemes(self) -> List:
#         """Load color schemes for charts"""
#         return ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#FF8A80', '#81C784']
    
#     def analyze_conversation_with_llm(self, conversation_history: List[Dict]) -> Dict:
#         """Use LLM to analyze conversation and extract event details intelligently"""
#         if not conversation_history:
#             return self._get_default_event_details()
        
#         conversation_text = self._prepare_conversation_text(conversation_history)
#         analysis_prompt = self._create_analysis_prompt(conversation_text)
        
#         try:
#             response = self._call_llm_api(analysis_prompt)
#             if response:
#                 event_details = self._parse_llm_response(response)
#                 return self._validate_event_details(event_details)
#         except Exception as e:
#             print(f"LLM analysis failed: {e}")
        
#         return self._basic_extraction(conversation_history)
    
#     def _prepare_conversation_text(self, conversation_history: List[Dict]) -> str:
#         """Prepare conversation text for analysis"""
#         conversation_text = ""
#         for msg in conversation_history:
#             role = msg.get("role", "")
#             content = msg.get("content", "").strip()
#             if content:
#                 conversation_text += f"{role.upper()}: {content}\n"
#         return conversation_text
    
#     def _create_analysis_prompt(self, conversation_text: str) -> str:
#         """Create dynamic analysis prompt"""
#         return f"""
# Analyze the following event planning conversation and extract key details in JSON format.

# Conversation:
# {conversation_text}

# Extract the following information and return ONLY a valid JSON object:
# {{
#     "event_type": "type of event (wedding, birthday, corporate, etc.)",
#     "guest_count": number_of_guests,
#     "venue": "specific venue name mentioned or 'To be determined'",
#     "venue_address": "venue address if mentioned",
#     "city": "city name",
#     "date": "event date or 'To be scheduled'",
#     "budget": total_budget_amount,
#     "budget_breakdown": {{
#         "category1": amount1,
#         "category2": amount2
#     }},
#     "vendors": ["list of specific vendor names mentioned"],
#     "key_decisions": ["important decisions made by user"],
#     "requirements": ["specific requirements mentioned by user"],
#     "user_preferences": ["user preferences and choices"]
# }}

# Focus on extracting actual numbers, names, and specific details mentioned in the conversation.
# """
    
#     def _call_llm_api(self, prompt: str) -> Optional[str]:
#         """Call LLM API with error handling"""
#         try:
#             response = requests.post(
#                 self.llm_url,
#                 headers={"Authorization": f"Bearer {self.llm_token}", "Content-Type": "application/json"},
#                 json={
#                     "model": "llama-3.1-8b-instant",
#                     "messages": [{"role": "user", "content": prompt}],
#                     "temperature": 0.1,
#                     "max_tokens": 1000
#                 },
#                 timeout=30
#             )
            
#             if response.status_code == 200:
#                 result = response.json()
#                 return result.get("choices", [{}])[0].get("message", {}).get("content", "")
#         except Exception as e:
#             print(f"API call failed: {e}")
#         return None
    
#     def _parse_llm_response(self, content: str) -> Dict:
#         """Parse LLM response to extract JSON"""
#         start_idx = content.find('{')
#         end_idx = content.rfind('}') + 1
#         if start_idx != -1 and end_idx != -1:
#             json_str = content[start_idx:end_idx]
#             return json.loads(json_str)
#         raise ValueError("No valid JSON found in response")
    
#     def _get_default_event_details(self) -> Dict:
#         """Return default event details structure"""
#         return {
#             "event_type": "Event Planning Consultation",
#             "guest_count": 0,
#             "venue": "To be determined",
#             "venue_address": "",
#             "date": "To be scheduled",
#             "budget": 0,
#             "budget_breakdown": {},
#             "vendors": [],
#             "key_decisions": [],
#             "user_preferences": [],
#             "city": "Not specified",
#             "requirements": [],
#             "timeline": "To be planned"
#         }
    
#     def _validate_event_details(self, details: Dict) -> Dict:
#         """Validate and clean extracted event details"""
#         default_details = self._get_default_event_details()
        
#         for key in default_details:
#             if key not in details:
#                 details[key] = default_details[key]
        
#         # Type validation
#         details["guest_count"] = int(details["guest_count"]) if isinstance(details["guest_count"], (int, str)) and str(details["guest_count"]).isdigit() else 0
#         details["budget"] = float(details["budget"]) if isinstance(details["budget"], (int, float, str)) and str(details["budget"]).replace('.', '').isdigit() else 0
        
#         if not isinstance(details["budget_breakdown"], dict):
#             details["budget_breakdown"] = {}
        
#         for list_key in ["vendors", "key_decisions", "requirements", "user_preferences"]:
#             if not isinstance(details[list_key], list):
#                 details[list_key] = []
        
#         return details
    
#     def _basic_extraction(self, conversation_history: List[Dict]) -> Dict:
#         """Basic fallback extraction method using patterns"""
#         event_details = self._get_default_event_details()
#         full_text = " ".join([msg.get("content", "") for msg in conversation_history]).lower()
        
#         # Dynamic event type detection
#         for event_type, patterns in self.event_type_patterns.items():
#             if any(pattern in full_text for pattern in patterns):
#                 event_details["event_type"] = event_type.title()
#                 break
        
#         # Extract numbers for guest count and budget
#         numbers = re.findall(r'\b\d+\b', full_text)
#         if numbers:
#             # Heuristic: larger numbers likely budget, smaller likely guest count
#             sorted_numbers = sorted([int(n) for n in numbers], reverse=True)
#             if sorted_numbers[0] > 1000:
#                 event_details["budget"] = sorted_numbers[0]
#             if len(sorted_numbers) > 1 and sorted_numbers[-1] < 1000:
#                 event_details["guest_count"] = sorted_numbers[-1]
        
#         return event_details
    
#     def extract_event_details_from_conversation(self, conversation_history: List[Dict]) -> Dict:
#         """Main method to extract event details using LLM analysis"""
#         return self.analyze_conversation_with_llm(conversation_history)
    
#     def generate_budget_breakdown(self, event_type: str, total_budget: int, guest_count: int) -> Tuple[Dict, int]:
#         """Generate realistic budget breakdown based on event type"""
#         if total_budget == 0:
#             per_person_estimates = {"wedding": 4000, "birthday": 1500, "corporate": 2000, "anniversary": 2500, "engagement": 3000}
#             total_budget = guest_count * per_person_estimates.get(event_type.lower(), 2000)
        
#         distribution = self.budget_distributions.get(event_type.lower(), self.budget_distributions["birthday"])
        
#         breakdown = {}
#         for category, percentage in distribution.items():
#             amount = int((percentage / 100) * total_budget)
#             breakdown[category.replace('_', ' ').title()] = {"amount": amount, "percentage": percentage}
        
#         return breakdown, total_budget
    
#     def create_budget_chart(self, budget_breakdown: Dict) -> str:
#         """Create enhanced budget visualization with pie chart and bar chart"""
#         if not DEPENDENCIES_AVAILABLE or not budget_breakdown:
#             return ""
        
#         try:
#             categories = list(budget_breakdown.keys())
#             amounts = [budget_breakdown[cat]["amount"] for cat in categories]
            
#             fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
#             colors_list = self.color_schemes[:len(categories)]
            
#             # Pie chart
#             wedges, texts, autotexts = ax1.pie(
#                 amounts, labels=categories, autopct='%1.1f%%',
#                 colors=colors_list, startangle=90, textprops={'fontsize': 10}
#             )
            
#             ax1.set_title('Budget Distribution', fontsize=14, fontweight='bold', pad=20)
            
#             for autotext in autotexts:
#                 autotext.set_color('white')
#                 autotext.set_fontweight('bold')
            
#             # Bar chart
#             bars = ax2.bar(categories, amounts, color=colors_list)
#             ax2.set_title('Budget Breakdown by Category', fontsize=14, fontweight='bold')
#             ax2.set_ylabel('Amount (₹)', fontsize=12)
#             ax2.tick_params(axis='x', rotation=45)
            
#             for bar, amount in zip(bars, amounts):
#                 height = bar.get_height()
#                 ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
#                         f'₹{amount:,}', ha='center', va='bottom', fontsize=9)
            
#             plt.tight_layout()
            
#             buffer = BytesIO()
#             plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
#             buffer.seek(0)
#             chart_base64 = base64.b64encode(buffer.getvalue()).decode()
#             plt.close()
            
#             return chart_base64
            
#         except Exception as e:
#             print(f"Chart generation error: {e}")
#             return ""
    
#     def _categorize_vendor(self, vendor_name: str) -> str:
#         """Dynamically categorize vendor based on name"""
#         vendor_lower = vendor_name.lower()
#         for category, keywords in self.vendor_categories.items():
#             if any(keyword in vendor_lower for keyword in keywords):
#                 return category.replace('_', ' ').title()
#         return "General Service"
    
#     def _create_pdf_styles(self) -> Dict:
#         """Create dynamic PDF styles"""
#         styles = getSampleStyleSheet()
#         return {
#             'title': ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=26,
#                                   spaceAfter=30, alignment=TA_CENTER, textColor=colors.HexColor('#2C3E50')),
#             'subtitle': ParagraphStyle('CustomSubtitle', parent=styles['Normal'], fontSize=14,
#                                      spaceAfter=20, alignment=TA_CENTER, textColor=colors.HexColor('#7F8C8D')),
#             'heading': ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=16,
#                                     spaceAfter=12, spaceBefore=20, textColor=colors.HexColor('#2C3E50')),
#             'normal': ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=11,
#                                    spaceAfter=6, alignment=TA_JUSTIFY),
#             'footer': ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9,
#                                    alignment=TA_CENTER, textColor=colors.HexColor('#7F8C8D'))
#         }
    
#     def generate_summary_pdf(self, event_details: Dict, conversation_id: str) -> str:
#         """Generate enhanced professional PDF event summary with better visualization"""
#         if not DEPENDENCIES_AVAILABLE:
#             return self.generate_summary_html(event_details, conversation_id)
        
#         try:
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             filename = f"event_summary_{conversation_id}_{timestamp}.pdf"
#             filepath = self.output_dir / filename
            
#             doc = SimpleDocTemplate(str(filepath), pagesize=A4, rightMargin=2*cm, leftMargin=2*cm,
#                                   topMargin=2*cm, bottomMargin=2*cm)
            
#             styles = self._create_pdf_styles()
#             story = []
            
#             # Header
#             story.append(Paragraph("EventMaster Pro", styles['title']))
#             story.append(Paragraph("Professional Event Planning Summary", styles['subtitle']))
#             story.append(Spacer(1, 20))
            
#             # Event Overview
#             story.append(Paragraph("Event Overview", styles['heading']))
#             overview_text = f"""
#             This comprehensive summary outlines the planning details for a {event_details['event_type'].lower()} 
#             designed for {event_details['guest_count']} guests. The consultation has been structured to ensure 
#             all aspects are covered within the specified requirements and budget considerations.
#             """
#             story.append(Paragraph(overview_text, styles['normal']))
#             story.append(Spacer(1, 15))
            
#             # Event Details Table
#             story.append(Paragraph("Event Details", styles['heading']))
#             details_data = self._create_details_table_data(event_details)
#             details_table = self._create_styled_table(details_data, [4*cm, 10*cm])
#             story.append(details_table)
#             story.append(Spacer(1, 20))
            
#             # Budget Analysis
#             if event_details['budget'] > 0:
#                 budget_breakdown, total_budget = self.generate_budget_breakdown(
#                     event_details['event_type'], event_details['budget'], event_details['guest_count']
#                 )
                
#                 story.append(Paragraph("Detailed Budget Analysis", styles['heading']))
#                 budget_table = self._create_budget_table(budget_breakdown, event_details['guest_count'])
#                 story.append(budget_table)
#                 story.append(Spacer(1, 15))
                
#                 # Budget Insights
#                 insights = self._generate_budget_insights(budget_breakdown, total_budget, event_details)
#                 story.append(Paragraph("Budget Insights & Recommendations", styles['heading']))
#                 for insight in insights:
#                     story.append(Paragraph(insight, styles['normal']))
            
#             # Vendor Selections
#             if event_details.get('vendors'):
#                 story.append(Spacer(1, 15))
#                 story.append(Paragraph("Selected Vendors & Services", styles['heading']))
#                 vendor_table = self._create_vendor_table(event_details['vendors'])
#                 story.append(vendor_table)
            
#             # Requirements & Decisions
#             if event_details.get('requirements') or event_details.get('key_decisions'):
#                 story.append(Spacer(1, 15))
#                 story.append(Paragraph("Key Requirements & Decisions", styles['heading']))
#                 req_table = self._create_requirements_table(event_details)
#                 story.append(req_table)
            
#             # Footer
#             story.extend(self._create_footer(conversation_id, styles['footer']))
            
#             doc.build(story)
#             return str(filepath)
            
#         except Exception as e:
#             print(f"PDF generation error: {e}")
#             return self.generate_summary_html(event_details, conversation_id)
    
#     def _create_details_table_data(self, event_details: Dict) -> List[List[str]]:
#         """Create details table data dynamically"""
#         data = [
#             ['Event Type', event_details['event_type']],
#             ['Guest Count', f"{event_details['guest_count']} people" if event_details['guest_count'] > 0 else "To be determined"],
#             ['Venue', event_details['venue']],
#             ['Location', event_details['city']],
#             ['Date', event_details['date']],
#             ['Total Budget', f"₹{event_details['budget']:,}" if event_details['budget'] > 0 else "To be finalized"]
#         ]
        
#         if event_details.get('venue_address'):
#             data.insert(4, ['Venue Address', event_details['venue_address']])
        
#         return data
    
#     def _create_styled_table(self, data: List[List[str]], col_widths: List) -> Table:
#         """Create styled table with dynamic formatting"""
#         table = Table(data, colWidths=col_widths)
#         table.setStyle(TableStyle([
#             ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#4ECDC4')),
#             ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
#             ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
#             ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
#             ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
#             ('FONTSIZE', (0, 0), (-1, -1), 10),
#             ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
#             ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E9ECEF')),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
#         ]))
#         return table
    
#     def _create_budget_table(self, budget_breakdown: Dict, guest_count: int) -> Table:
#         """Create budget table dynamically"""
#         budget_data = [['Category', 'Amount (₹)', '% of Total', 'Per Guest (₹)']]
#         total_amount = 0
        
#         for category, details in budget_breakdown.items():
#             amount = details['amount']
#             percentage = details['percentage']
#             per_guest = amount // guest_count if guest_count > 0 else 0
#             budget_data.append([category, f"₹{amount:,}", f"{percentage}%", f"₹{per_guest:,}"])
#             total_amount += amount
        
#         total_per_guest = total_amount // guest_count if guest_count > 0 else 0
#         budget_data.append(['Total', f"₹{total_amount:,}", "100%", f"₹{total_per_guest:,}"])
        
#         budget_table = Table(budget_data, colWidths=[4*cm, 3*cm, 2.5*cm, 3*cm])
#         budget_table.setStyle(TableStyle([
#             ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4ECDC4')),
#             ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#             ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
#             ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
#             ('FONTSIZE', (0, 0), (-1, -1), 9),
#             ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F8F9FA')]),
#             ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E9ECEF')),
#             ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E9ECEF')),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
#         ]))
#         return budget_table
    
#     def _generate_budget_insights(self, budget_breakdown: Dict, total_budget: int, event_details: Dict) -> List[str]:
#         """Generate dynamic budget insights"""
#         cost_per_guest = total_budget // event_details['guest_count'] if event_details['guest_count'] > 0 else 0
#         largest_category = max(budget_breakdown.items(), key=lambda x: x[1]['amount'])
        
#         return [
#             f"• Average cost per guest: ₹{cost_per_guest:,} per person",
#             f"• Largest expense category: {largest_category[0]} ({largest_category[1]['percentage']}% of total budget)",
#             f"• Budget distribution: Well-balanced across {len(budget_breakdown)} essential categories",
#             f"• Cost efficiency: {event_details['event_type']} events typically range ₹{cost_per_guest-500:,}-₹{cost_per_guest+500:,} per guest",
#             f"• Recommendation: Book vendors 2-3 months in advance for better rates and availability"
#         ]
    
#     def _create_vendor_table(self, vendors: List[str]) -> Table:
#         """Create vendor table dynamically"""
#         vendor_data = [['Service Category', 'Vendor Name', 'Status']]
#         for vendor in vendors:
#             service_type = self._categorize_vendor(vendor)
#             vendor_data.append([service_type, vendor, "Confirmed"])
        
#         if len(vendor_data) > 1:
#             vendor_table = Table(vendor_data, colWidths=[4*cm, 6*cm, 3*cm])
#             vendor_table.setStyle(TableStyle([
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4ECDC4')),
#                 ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                 ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 10),
#                 ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
#                 ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E9ECEF')),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
#             ]))
#             return vendor_table
#         return Table([])
    
#     def _create_requirements_table(self, event_details: Dict) -> Table:
#         """Create requirements table dynamically"""
#         req_data = [['Type', 'Details']]
        
#         for req in event_details.get('requirements', [])[:3]:
#             if len(req.strip()) > 10:
#                 req_data.append(['Requirement', req.strip()[:100] + '...' if len(req) > 100 else req.strip()])
        
#         for decision in event_details.get('key_decisions', [])[:3]:
#             if len(decision.strip()) > 10:
#                 req_data.append(['Decision', decision.strip()[:100] + '...' if len(decision) > 100 else decision.strip()])
        
#         if len(req_data) > 1:
#             req_table = Table(req_data, colWidths=[3*cm, 10*cm])
#             req_table.setStyle(TableStyle([
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4ECDC4')),
#                 ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                 ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 10),
#                 ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
#                 ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E9ECEF')),
#                 ('VALIGN', (0, 0), (-1, -1), 'TOP')
#             ]))
#             return req_table
#         return Table([])
    
#     def _create_footer(self, conversation_id: str, footer_style) -> List:
#         """Create footer elements dynamically"""
#         return [
#             Spacer(1, 30),
#             Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", footer_style),
#             Paragraph("EventMaster Pro - AI-Powered Event Planning Assistant", footer_style),
#             Paragraph(f"Document ID: {conversation_id}", footer_style)
#         ]
    
#     def generate_summary_html(self, event_details: Dict, conversation_id: str) -> str:
#         """Generate HTML summary document dynamically"""
#         budget_breakdown, total_budget = self.generate_budget_breakdown(
#             event_details["event_type"], event_details["budget"], event_details["guest_count"]
#         )
        
#         chart_base64 = self.create_budget_chart(budget_breakdown)
#         per_person_cost = total_budget // event_details["guest_count"] if event_details["guest_count"] > 0 else 0
        
#         # Dynamic HTML generation
#         html_content = self._create_html_template(event_details, budget_breakdown, total_budget, 
#                                                 per_person_cost, chart_base64, conversation_id)
        
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"event_summary_{conversation_id}_{timestamp}.html"
#         filepath = self.output_dir / filename
        
#         with open(filepath, 'w', encoding='utf-8') as f:
#             f.write(html_content)
        
#         return str(filepath)
    
#     def _create_html_template(self, event_details: Dict, budget_breakdown: Dict, total_budget: int,
#                             per_person_cost: int, chart_base64: str, conversation_id: str) -> str:
#         """Create HTML template dynamically"""
#         budget_rows = self._generate_budget_rows(budget_breakdown)
#         chart_section = f'<img src="data:image/png;base64,{chart_base64}" alt="Budget Distribution Chart">' if chart_base64 else '<p>Budget visualization not available</p>'
#         largest_expense = max(budget_breakdown.keys(), key=lambda x: budget_breakdown[x]["amount"]) if budget_breakdown else "N/A"
#         largest_percentage = max(budget_breakdown.values(), key=lambda x: x["amount"])["percentage"] if budget_breakdown else 0
        
#         return f"""
#         <!DOCTYPE html>
#         <html lang="en">
#         <head>
#             <meta charset="UTF-8">
#             <meta name="viewport" content="width=device-width, initial-scale=1.0">
#             <title>Event Planning Summary</title>
#             <style>{self._get_html_styles()}</style>
#         </head>
#         <body>
#             <div class="container">
#                 <div class="header">
#                     <h1>{event_details["event_type"]} Planning Summary</h1>
#                     <p>Generated on {datetime.now().strftime("%B %d, %Y")}</p>
#                     <p>EventBot - AI Event Planning Assistant</p>
#                 </div>
                
#                 <div class="section">
#                     <div class="overview">
#                         <h2>Event Overview</h2>
#                         <p>This comprehensive summary outlines the planning details for a {event_details["event_type"].lower()} 
#                         designed for {event_details["guest_count"]} guests. The event planning process has been carefully 
#                         structured to ensure all aspects are covered within the specified budget and requirements.</p>
#                     </div>
#                 </div>
                
#                 <div class="section">
#                     <h2>Event Details</h2>
#                     <div class="details-grid">
#                         <div class="detail-card">
#                             <h3>Event Type</h3>
#                             <p>{event_details["event_type"]}</p>
#                         </div>
#                         <div class="detail-card">
#                             <h3>Guest Count</h3>
#                             <p>{event_details["guest_count"]} people</p>
#                         </div>
#                         <div class="detail-card">
#                             <h3>Venue</h3>
#                             <p>{event_details["venue"]}</p>
#                         </div>
#                         <div class="detail-card">
#                             <h3>Total Budget</h3>
#                             <p>Rupees {total_budget:,}</p>
#                         </div>
#                     </div>
#                 </div>
                
#                 <div class="section">
#                     <h2>Budget Analysis</h2>
#                     <div class="budget-section">
#                         <div>
#                             <table class="budget-table">
#                                 <thead>
#                                     <tr>
#                                         <th>Category</th>
#                                         <th>Amount (Rupees)</th>
#                                         <th>% of Total</th>
#                                     </tr>
#                                 </thead>
#                                 <tbody>
#                                     {budget_rows}
#                                     <tr class="total-row">
#                                         <td><strong>Total</strong></td>
#                                         <td><strong>Rupees {total_budget:,}</strong></td>
#                                         <td><strong>100%</strong></td>
#                                     </tr>
#                                 </tbody>
#                             </table>
#                         </div>
#                         <div class="chart-container">
#                             {chart_section}
#                         </div>
#                     </div>
#                 </div>
                
#                 <div class="section">
#                     <div class="insights">
#                         <h2>Key Insights</h2>
#                         <ul>
#                             <li><strong>Cost per guest:</strong> Rupees {per_person_cost:,} per person</li>
#                             <li><strong>Largest expense:</strong> {largest_expense} ({largest_percentage}% of total budget)</li>
#                             <li><strong>Budget efficiency:</strong> Well-distributed across essential categories</li>
#                             <li><strong>Recommendation:</strong> Consider booking vendors early to secure better rates</li>
#                         </ul>
#                     </div>
#                 </div>
                
#                 <div class="footer">
#                     <p>Document ID: {conversation_id}</p>
#                     <p>This summary was generated by EventBot AI Assistant based on your conversation.</p>
#                     <p>For questions or modifications, please contact your event planning assistant.</p>
#                 </div>
#             </div>
#         </body>
#         </html>
#         """
    
#     def _generate_budget_rows(self, budget_breakdown: Dict) -> str:
#         """Generate budget table rows dynamically"""
#         rows = ""
#         for category, details in budget_breakdown.items():
#             rows += f"""
#                 <tr>
#                     <td>{category}</td>
#                     <td>{details["amount"]:,}</td>
#                     <td>{details["percentage"]}%</td>
#                 </tr>
#             """
#         return rows
    
#     def _get_html_styles(self) -> str:
#         """Get HTML styles dynamically"""
#         return """
#                 body {
#                     font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#                     line-height: 1.6;
#                     margin: 0;
#                     padding: 20px;
#                     background-color: #f8f9fa;
#                     color: #333;
#                 }
#                 .container {
#                     max-width: 800px;
#                     margin: 0 auto;
#                     background: white;
#                     padding: 30px;
#                     border-radius: 10px;
#                     box-shadow: 0 4px 6px rgba(0,0,0,0.1);
#                 }
#                 .header {
#                     text-align: center;
#                     border-bottom: 3px solid #4ECDC4;
#                     padding-bottom: 20px;
#                     margin-bottom: 30px;
#                 }
#                 .header h1 {
#                     color: #2C3E50;
#                     margin: 0;
#                     font-size: 28px;
#                 }
#                 .header p {
#                     color: #7F8C8D;
#                     margin: 5px 0;
#                 }
#                 .section {
#                     margin-bottom: 25px;
#                 }
#                 .section h2 {
#                     color: #2C3E50;
#                     border-left: 4px solid #4ECDC4;
#                     padding-left: 15px;
#                     margin-bottom: 15px;
#                 }
#                 .overview {
#                     background: #ECF0F1;
#                     padding: 20px;
#                     border-radius: 8px;
#                     margin-bottom: 20px;
#                 }
#                 .details-grid {
#                     display: grid;
#                     grid-template-columns: 1fr 1fr;
#                     gap: 20px;
#                     margin-bottom: 20px;
#                 }
#                 .detail-card {
#                     background: #F8F9FA;
#                     padding: 15px;
#                     border-radius: 8px;
#                     border-left: 4px solid #4ECDC4;
#                 }
#                 .detail-card h3 {
#                     margin: 0 0 10px 0;
#                     color: #2C3E50;
#                 }
#                 .detail-card p {
#                     margin: 0;
#                     font-size: 16px;
#                     font-weight: 500;
#                 }
#                 .budget-section {
#                     display: grid;
#                     grid-template-columns: 1fr 1fr;
#                     gap: 30px;
#                     align-items: start;
#                 }
#                 .budget-table {
#                     width: 100%;
#                     border-collapse: collapse;
#                     margin-top: 10px;
#                 }
#                 .budget-table th, .budget-table td {
#                     padding: 12px;
#                     text-align: left;
#                     border-bottom: 1px solid #ddd;
#                 }
#                 .budget-table th {
#                     background-color: #4ECDC4;
#                     color: white;
#                     font-weight: 600;
#                 }
#                 .budget-table tr:nth-child(even) {
#                     background-color: #f9f9f9;
#                 }
#                 .total-row {
#                     font-weight: bold;
#                     background-color: #E8F6F3 !important;
#                 }
#                 .chart-container {
#                     text-align: center;
#                 }
#                 .chart-container img {
#                     max-width: 100%;
#                     height: auto;
#                     border-radius: 8px;
#                 }
#                 .insights {
#                     background: #E8F6F3;
#                     padding: 20px;
#                     border-radius: 8px;
#                     border-left: 4px solid #27AE60;
#                 }
#                 .insights ul {
#                     margin: 0;
#                     padding-left: 20px;
#                 }
#                 .insights li {
#                     margin-bottom: 8px;
#                 }
#                 .footer {
#                     text-align: center;
#                     margin-top: 30px;
#                     padding-top: 20px;
#                     border-top: 1px solid #ddd;
#                     color: #7F8C8D;
#                 }
#                 @media print {
#                     body { background: white; }
#                     .container { box-shadow: none; }
#                 }
#         """
    
#     def save_summary(self, conversation_data: Dict, format_type: str = "pdf") -> Dict:
#         """Generate and save enhanced event summary with LLM analysis"""
#         try:
#             conversation_history = conversation_data.get("conversation_history", [])
#             agent_id = conversation_data.get("agent_id", "unknown")
            
#             event_details = self.extract_event_details_from_conversation(conversation_history)
            
#             if format_type.lower() == "pdf" and DEPENDENCIES_AVAILABLE:
#                 filepath = self.generate_summary_pdf(event_details, agent_id)
#                 filename = Path(filepath).name
#                 url = f"/summary/download/{filename}"
#             else:
#                 filepath = self.generate_summary_html(event_details, agent_id)
#                 filename = Path(filepath).name
#                 url = f"/summary/view/{filename}"
            
#             return {
#                 "success": True,
#                 "filename": filename,
#                 "filepath": str(filepath),
#                 "event_details": event_details,
#                 "url": url,
#                 "format": "pdf" if str(filepath).endswith('.pdf') else "html",
#                 "extraction_method": "llm_analysis"
#             }
            
#         except Exception as e:
#             return {"success": False, "error": str(e)}

# # Global instance
# summary_generator = EventSummaryGenerator()

# def generate_event_summary(conversation_data: Dict) -> Dict:
#     """Generate enhanced event summary using LLM analysis"""
#     return summary_generator.save_summary(conversation_data)


"""
SmartEvent AI Saathi - Professional Event Summary Generator
Creates comprehensive PDF event planning summaries with budget visualization
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import base64
from io import BytesIO

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.pdfgen import canvas
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    print("⚠️ PDF generation dependencies not available. Install: pip install matplotlib reportlab")

class EventSummaryGenerator:
    def __init__(self):
        self.output_dir = Path("event_summaries")
        self.output_dir.mkdir(exist_ok=True)
    
    def extract_event_details_from_conversation(self, conversation_history: List[Dict]) -> Dict:
        """Enhanced extraction of event details from conversation history"""
        event_details = {
            "event_type": "Event Planning Consultation",
            "guest_count": 0,
            "venue": "To be determined",
            "venue_address": "",
            "date": "To be scheduled",
            "budget": 0,
            "budget_breakdown": {},
            "vendors": [],
            "key_decisions": [],
            "user_preferences": [],
            "city": "Not specified",
            "requirements": [],
            "timeline": "To be planned",
            "cuisine": "Not specified"
        }
        
        print(f"🔍 DEBUG: Processing conversation with {len(conversation_history)} messages")
        for i, msg in enumerate(conversation_history):
            print(f"🔍 DEBUG: Message {i}: Role={msg.get('role')}, Content={msg.get('content', '')[:100]}...")
        
        if not conversation_history:
            return event_details
        
        # Combine all conversation content
        user_messages = []
        assistant_messages = []
        
        for msg in conversation_history:
            content = msg.get("content", "").strip()
            if not content:
                continue
                
            role = msg.get("role", "")
            if role == "user":
                user_messages.append(content)
            elif role == "assistant":
                assistant_messages.append(content)
        
        full_conversation = " ".join(user_messages + assistant_messages)
        user_input = " ".join(user_messages)
        
        # Enhanced event type detection - prioritize user's exact words
        event_patterns = {
            "Family Get Together": ["family get together", "family gathering", "family reunion", "family meet", "chhota sa family", "परिवार का मिलन", "परिवार की मिलन"],
            "Birthday Party": ["birthday", "bday", "birth anniversary", "birthday party", "जन्मदिन"],
            "Wedding": ["wedding", "marriage", "shaadi", "bride", "groom", "matrimony", "शादी"],
            "Corporate Event": ["corporate", "company", "business", "office", "conference", "meeting"],
            "Anniversary": ["anniversary", "celebration", "सालगिरह"],
            "Engagement": ["engagement", "ring ceremony", "sagai", "सगाई"],
            "Reception": ["reception", "party"],
            "Baby Shower": ["baby shower", "godh bharai", "गोद भराई"],
            "Graduation": ["graduation", "convocation"]
        }
        
        # Look for event type in user messages first (user's actual words)
        for msg in user_messages:
            msg_lower = msg.lower()
            print(f"🔍 DEBUG: Checking event type in user message: {msg_lower}")
            for event_type, keywords in event_patterns.items():
                if any(keyword in msg_lower for keyword in keywords):
                    event_details["event_type"] = event_type
                    print(f"🔍 DEBUG: Found event type: {event_type}")
                    break
            if event_details["event_type"] != "Event Planning Consultation":
                break
        
        # If not found in user messages, check assistant messages for confirmation
        if event_details["event_type"] == "Event Planning Consultation":
            for msg in assistant_messages:
                msg_lower = msg.lower()
                for event_type, keywords in event_patterns.items():
                    if any(keyword in msg_lower for keyword in keywords):
                        event_details["event_type"] = event_type
                        print(f"🔍 DEBUG: Found event type in assistant message: {event_type}")
                        break
                if event_details["event_type"] != "Event Planning Consultation":
                    break
        
        # Enhanced guest count extraction - prioritize user's explicit mentions
        guest_patterns = [
            r'(\d+)\s*(?:people|guests|persons|attendees|pax|members)',
            r'around\s*(\d+)',
            r'approximately\s*(\d+)',
            r'about\s*(\d+)\s*(?:people|guests)',
            r'for\s*(\d+)\s*(?:people|guests)',
            r'(\d+)\s*family\s*members',
            r'total\s*(\d+)',
        ]
        
        # Look for guest count in user messages with context
        for msg in user_messages:
            msg_lower = msg.lower().strip()
            print(f"🔍 DEBUG: Checking guest count in: {msg_lower}")
            
            # Handle Hindi numbers
            hindi_numbers = {
                'ek': 1, 'do': 2, 'teen': 3, 'char': 4, 'panch': 5,
                'chhe': 6, 'saat': 7, 'aath': 8, 'nau': 9, 'dus': 10,
                'gyarah': 11, 'barah': 12, 'terah': 13, 'chaudah': 14, 'pandrah': 15,
                'solah': 16, 'satrah': 17, 'atharah': 18, 'unnis': 19, 'bees': 20,
                'pachas': 50, 'sau': 100
            }
            
            # Check for Hindi numbers with context (people/log)
            if any(word in msg_lower for word in ['log', 'people', 'guests', 'persons']):
                for hindi_word, number in hindi_numbers.items():
                    if hindi_word in msg_lower:
                        if 1 <= number <= 10000:
                            event_details["guest_count"] = number
                            print(f"🔍 DEBUG: Found guest count (Hindi with context): {number}")
                            break
                
                if event_details["guest_count"] > 0:
                    break
            
            # Check for English number patterns
            for pattern in guest_patterns:
                matches = re.findall(pattern, msg_lower)
                if matches:
                    try:
                        count = int(matches[-1])
                        if 1 <= count <= 10000:  # Reasonable range
                            event_details["guest_count"] = count
                            print(f"🔍 DEBUG: Found guest count: {count}")
                            break
                    except ValueError:
                        continue
            if event_details["guest_count"] > 0:
                break
        
        # Enhanced venue extraction - prioritize user's actual venue selections
        venue_patterns = [
            # Direct venue name patterns - only match actual venue names
            r'(?:book|select|choose|want|prefer|decided|going with)\s+([A-Z][a-zA-Z\s&\-\']+(?:Hotel|Resort|Banquet|Hall|Palace|Center|Manor|Gardens?|Haveli))',
            r'(Hotel\s+[A-Z][a-zA-Z\s&\-\']+)',
            r'([A-Z][a-zA-Z\s&\-\']+\s+(?:Hotel|Resort|Banquet|Hall|Palace|Center|Manor|Gardens?))',
            r'(Haveli)',
            r'([A-Z][a-zA-Z\s]*\s+Garden)',
            r'(Garden\s+[A-Z][a-zA-Z\s]*)',
            r'(?:at|in)\s+([A-Z][a-zA-Z\s&\-\']+(?:Hotel|Resort|Banquet|Hall|Palace|Center|Manor|Gardens?|Haveli))'
        ]
        
        # Look for venue names in user messages - find the LATEST mention
        latest_venue = None
        latest_venue_index = -1
        
        # First, check if user made a specific venue selection
        for i, msg in enumerate(user_messages):
            msg_clean = msg.strip().lower()
            
            # Skip very short messages
            if len(msg_clean) < 5:
                continue
            
            # Check for specific venue selection phrases
            selection_phrases = ['book', 'select', 'choose', 'want', 'prefer', 'decided', 'going with', 'take', 'pick']
            if any(phrase in msg_clean for phrase in selection_phrases):
                # Look for venue patterns in this message
                for pattern in venue_patterns:
                    matches = re.findall(pattern, msg, re.IGNORECASE)
                    if matches:
                        venue_name = matches[-1].strip().title()
                        # Validate venue name
                        if (len(venue_name) > 3 and 
                            venue_name.lower() not in ['kanpur', 'mumbai', 'delhi', 'bangalore', 'chennai', 'can you', 'you hear', 'venue to plan', 'birthday event'] and
                            not venue_name.lower().startswith('can you') and
                            not venue_name.lower().startswith('you hear') and
                            not venue_name.lower().startswith('venue to')):
                            if latest_venue_index < i:
                                latest_venue = venue_name
                                latest_venue_index = i
                                print(f"🔍 DEBUG: Found venue selection: {venue_name}")
        
        # If no specific selection found, check for venue mentions in context
        if not latest_venue:
            for i, msg in enumerate(user_messages):
                msg_clean = msg.strip().lower()
                
                # Check for specific venue mentions
                if 'leela palace' in msg_clean:
                    latest_venue = "Leela Palace"
                    latest_venue_index = i
                elif 'leela garden' in msg_clean:
                    if latest_venue_index < i:
                        latest_venue = "Leela Garden"
                        latest_venue_index = i
                elif 'lush garden' in msg_clean or 'hear lush garden' in msg_clean:
                    if latest_venue_index < i:
                        latest_venue = "Lush Garden"
                        latest_venue_index = i
        
        # Set the latest venue found
        if latest_venue:
            event_details["venue"] = latest_venue
            print(f"🔍 DEBUG: Final venue set to: {latest_venue}")
        else:
            # Check if conversation is still in progress (no venue selected yet)
            conversation_text = " ".join(user_messages + assistant_messages).lower()
            if any(phrase in conversation_text for phrase in ['options', 'suggest', 'recommend', 'which one', 'कौन सा']):
                event_details["venue"] = "Selection in progress"
                print(f"🔍 DEBUG: Venue selection still in progress")
            else:
                event_details["venue"] = "To be determined"
                print(f"🔍 DEBUG: No venue found, keeping default")
        
        # Enhanced budget extraction - look for specific budget mentions
        budget_patterns = [
            # Look for explicit total budget mentions first
            r'budget.*?is.*?(\d+(?:,\d+)*)',
            r'budget.*?(\d+(?:,\d+)*)',
            r'i\s+have.*?(\d+(?:,\d+)*)',
            r'my\s+budget.*?(\d+(?:,\d+)*)',
            r'₹\s*(\d+(?:,\d+)*)',
            r'(\d+(?:,\d+)*)\s*rupees?',
            r'(\d+)\s*thousand',  # Handle thousands
            r'(\d+)\s*lakh',      # Handle lakhs
            r'(\d+)\s*crore',     # Handle crores
            r'(\d+(?:,\d+)*)\s*only',
            r'(\d+(?:,\d+)*)\s*rs',
        ]
        
        # Look for budget in user messages with priority order
        total_budget = 0
        budget_components = {}
        
        # First pass - look for explicit budget mentions in user messages
        for msg in user_messages:
            msg_lower = msg.lower().strip()
            print(f"🔍 DEBUG: Checking budget in: {msg_lower}")
            
            # Skip very short messages
            if len(msg_lower) < 3:
                continue
            
            # Priority 1: Look for "budget is X" patterns
            if 'budget' in msg_lower and any(char.isdigit() for char in msg_lower):
                for pattern in budget_patterns:
                    matches = re.findall(pattern, msg_lower)
                    if matches:
                        try:
                            amount_str = matches[-1].replace(',', '')
                            amount = int(amount_str)
                            
                            # Handle multipliers
                            if 'thousand' in msg_lower:
                                amount *= 1000
                            elif 'lakh' in msg_lower:
                                amount *= 100000
                            elif 'crore' in msg_lower:
                                amount *= 10000000
                            
                            # Validate reasonable budget range
                            if 1000 <= amount <= 100000000:
                                total_budget = amount
                                print(f"🔍 DEBUG: Found budget: ₹{amount:,}")
                                break
                        except (ValueError, IndexError):
                            continue
                
                if total_budget > 0:
                    break
            
            # Priority 2: Look for Hindi budget patterns
            elif 'hazar' in msg_lower or 'lakh' in msg_lower or 'crore' in msg_lower or 'rupee' in msg_lower:
                # Handle Hindi numbers
                hindi_numbers = {
                    'ek': 1, 'do': 2, 'teen': 3, 'char': 4, 'panch': 5,
                    'chhe': 6, 'saat': 7, 'aath': 8, 'nau': 9, 'dus': 10,
                    'gyarah': 11, 'barah': 12, 'terah': 13, 'chaudah': 14, 'pandrah': 15,
                    'solah': 16, 'satrah': 17, 'atharah': 18, 'unnis': 19, 'bees': 20,
                    'pachas': 50, 'sau': 100
                }
                
                # Look for Hindi number + multiplier patterns
                for hindi_word, number in hindi_numbers.items():
                    if hindi_word in msg_lower:
                        amount = number
                        if 'hazar' in msg_lower:
                            amount *= 1000
                        elif 'lakh' in msg_lower:
                            amount *= 100000
                        elif 'crore' in msg_lower:
                            amount *= 10000000
                        
                        if 1000 <= amount <= 100000000:
                            total_budget = amount
                            print(f"🔍 DEBUG: Found budget (Hindi): ₹{amount:,}")
                            break
                
                if total_budget > 0:
                    break
            
            # Priority 3: Look for "I have X" patterns
            elif ('i have' in msg_lower or 'my budget' in msg_lower) and any(char.isdigit() for char in msg_lower):
                for pattern in budget_patterns:
                    matches = re.findall(pattern, msg_lower)
                    if matches:
                        try:
                            amount_str = matches[-1].replace(',', '')
                            amount = int(amount_str)
                            
                            # Handle multipliers
                            if 'thousand' in msg_lower:
                                amount *= 1000
                            elif 'lakh' in msg_lower:
                                amount *= 100000
                            elif 'crore' in msg_lower:
                                amount *= 10000000
                            
                            if 1000 <= amount <= 100000000:
                                total_budget = amount
                                print(f"🔍 DEBUG: Found budget from 'I have': ₹{amount:,}")
                                break
                        except (ValueError, IndexError):
                            continue
                
                if total_budget > 0:
                    break
        
        # Second pass - if no total budget found, look for any budget numbers
        if total_budget == 0:
            for msg in user_messages:
                msg_lower = msg.lower().strip()
                
                # Look for standalone numbers that could be budget
                for pattern in budget_patterns:
                    matches = re.findall(pattern, msg_lower)
                    if matches:
                        try:
                            amount_str = matches[-1].replace(',', '')
                            amount = int(amount_str)
                            
                            # Handle multipliers
                            if 'thousand' in msg_lower:
                                amount *= 1000
                            elif 'lakh' in msg_lower:
                                amount *= 100000
                            elif 'crore' in msg_lower:
                                amount *= 10000000
                            
                            # Validate reasonable budget range
                            if 1000 <= amount <= 100000000:
                                total_budget = amount
                                break
                        except (ValueError, IndexError):
                            continue
                
                if total_budget > 0:
                    break
        
        if total_budget > 0:
            event_details["budget"] = total_budget
            
            # Create simple budget breakdown if specific components not found
            if not budget_components:
                budget_components = {
                    'Venue': int(total_budget * 0.4),
                    'Food & Catering': int(total_budget * 0.35),
                    'Decoration': int(total_budget * 0.15),
                    'Miscellaneous': int(total_budget * 0.1)
                }
            event_details["budget_breakdown"] = budget_components
        
        # Enhanced city extraction
        cities = {
            'kanpur': ['kanpur', 'cawnpore'],
            'mumbai': ['mumbai', 'bombay'],
            'delhi': ['delhi', 'new delhi'],
            'bangalore': ['bangalore', 'bengaluru'],
            'chennai': ['chennai', 'madras'],
            'hyderabad': ['hyderabad'],
            'pune': ['pune'],
            'kolkata': ['kolkata', 'calcutta'],
            'gurgaon': ['gurgaon', 'gurugram'],
            'noida': ['noida'],
            'ahmedabad': ['ahmedabad'],
            'jaipur': ['jaipur'],
            'lucknow': ['lucknow']
        }
        
        for city, variations in cities.items():
            if any(var in full_conversation.lower() for var in variations):
                event_details["city"] = city.title()
                break
        
        # Extract vendor decisions - prioritize user confirmations
        vendor_patterns = [
            r'(Coastal\s+Delight[s]?\s+Catering)',
            r'(Elegant\s+Occasions)',
            r'(Hotel\s+Gaurav)',
            r'(Hotel\s+Clarks?\s+Avadh)',
            r'([A-Z][a-zA-Z\s]+\s+(?:Catering|Decorat))',
            r'([A-Z][a-zA-Z\s]+\s+(?:Caterer|Decorator)s?)'
        ]
        
        # Look for confirmed vendor selections in assistant messages (recommendations)
        confirmed_vendors = []
        
        # Extract vendors mentioned by assistant that user might have confirmed
        for msg in assistant_messages:
            for pattern in vendor_patterns:
                matches = re.findall(pattern, msg, re.IGNORECASE)
                if matches:
                    for match in matches:
                        vendor_name = match.strip()
                        # Clean up vendor name
                        if (len(vendor_name) > 5 and 
                            vendor_name not in confirmed_vendors and
                            not vendor_name.lower().startswith('uh ') and
                            'decorat' not in vendor_name.lower() or 'decorator' in vendor_name.lower()):
                            confirmed_vendors.append(vendor_name)
        
        # Only keep the first few relevant vendors to avoid clutter
        event_details["vendors"] = confirmed_vendors[:3]
        
        # Extract key decisions from user confirmations
        decision_keywords = ["fine for me", "better choice", "make it done", "ok", "yeah", "good"]
        for i, msg in enumerate(user_messages):
            msg_lower = msg.lower()
            if any(keyword in msg_lower for keyword in decision_keywords):
                # Look at the previous assistant message for context
                if i > 0 and i < len(assistant_messages):
                    context = assistant_messages[i-1] if i-1 < len(assistant_messages) else ""
                    event_details["key_decisions"].append(f"Confirmed: {msg.strip()}")
        
        # Extract cuisine preferences - prioritize user's explicit mentions
        cuisine_patterns = [
            r'(?:i want|i prefer|give me).*?(indian cuisine|north indian|south indian|chinese|continental|italian|punjabi|gujarati|bengali|rajasthani|mughlai)',
            r'(indian cuisine|north indian|south indian|chinese|continental|italian|punjabi|gujarati|bengali|rajasthani|mughlai).*?(?:cuisine|food|menu|vendor)',
            r'(?:cuisine|food|menu).*?(indian cuisine|north indian|south indian|chinese|continental|italian|punjabi|gujarati|bengali|rajasthani|mughlai)',
            r'(?:prefer|want|like).*?(indian cuisine|north indian|south indian|chinese|continental|italian|punjabi|gujarati|bengali|rajasthani|mughlai)',
            r'(vegetarian|non-vegetarian|veg|non-veg)'
        ]
        
        # Look for cuisine in user messages first
        for msg in user_messages:
            msg_lower = msg.lower()
            for pattern in cuisine_patterns:
                matches = re.findall(pattern, msg_lower)
                if matches:
                    cuisine = matches[-1].strip().title()
                    if cuisine == 'Veg':
                        cuisine = 'Vegetarian'
                    elif cuisine == 'Non-Veg':
                        cuisine = 'Non-Vegetarian'
                    elif 'indian cuisine' in cuisine.lower():
                        cuisine = 'Indian'
                    event_details["cuisine"] = cuisine
                    break
            if event_details["cuisine"] != "Not specified":
                break
        
        # Extract requirements and preferences
        requirement_keywords = ["need", "want", "require", "looking for", "prefer", "important", "flower decoration", "separate caterer"]
        for msg in user_messages:
            msg_lower = msg.lower()
            if any(keyword in msg_lower for keyword in requirement_keywords):
                event_details["requirements"].append(msg.strip())
        
        return event_details
    
    def generate_budget_breakdown(self, event_type: str, total_budget: int, guest_count: int) -> Dict:
        """Generate realistic budget breakdown based on event type"""
        if total_budget == 0:
            # Estimate budget if not provided
            per_person_estimates = {
                "wedding": 4000,
                "birthday": 1500,
                "corporate": 2000,
                "anniversary": 2500,
                "engagement": 3000
            }
            total_budget = guest_count * per_person_estimates.get(event_type.lower(), 2000)
        
        # Budget distribution percentages by event type
        distributions = {
            "wedding": {
                "Venue": 35,
                "Catering": 30,
                "Decoration": 15,
                "Photography": 10,
                "Entertainment": 5,
                "Miscellaneous": 5
            },
            "birthday": {
                "Venue": 25,
                "Catering": 40,
                "Decoration": 20,
                "Entertainment": 10,
                "Miscellaneous": 5
            },
            "corporate": {
                "Venue": 30,
                "Catering": 35,
                "AV Equipment": 15,
                "Materials": 10,
                "Transportation": 5,
                "Miscellaneous": 5
            }
        }
        
        distribution = distributions.get(event_type.lower(), distributions["birthday"])
        
        breakdown = {}
        for category, percentage in distribution.items():
            amount = int((percentage / 100) * total_budget)
            breakdown[category] = {
                "amount": amount,
                "percentage": percentage
            }
        
        return breakdown, total_budget
    
    def create_budget_chart(self, budget_breakdown: Dict) -> str:
        """Create a pie chart for budget breakdown and return base64 encoded image"""
        if not DEPENDENCIES_AVAILABLE:
            return ""
        
        try:
            # Prepare data
            categories = list(budget_breakdown.keys())
            amounts = [budget_breakdown[cat]["amount"] for cat in categories]
            percentages = [budget_breakdown[cat]["percentage"] for cat in categories]
            
            # Create pie chart
            fig, ax = plt.subplots(figsize=(6, 6))
            colors_list = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
            
            wedges, texts, autotexts = ax.pie(
                amounts, 
                labels=categories, 
                autopct='%1.1f%%',
                colors=colors_list[:len(categories)],
                startangle=90
            )
            
            # Styling
            ax.set_title('Budget Distribution', fontsize=14, fontweight='bold', pad=20)
            
            # Make text more readable
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            plt.tight_layout()
            
            # Save to base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return chart_base64
            
        except Exception as e:
            print(f"Chart generation error: {e}")
            return ""
    
    def generate_summary_pdf(self, event_details: Dict, conversation_id: str) -> str:
        """Generate professional PDF event summary"""
        if not DEPENDENCIES_AVAILABLE:
            return self.generate_summary_html(event_details, conversation_id)
        
        try:
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"event_summary_{conversation_id}_{timestamp}.pdf"
            filepath = self.output_dir / filename
            
            # Create PDF document
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#2C3E50')
            )
            
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Normal'],
                fontSize=14,
                spaceAfter=20,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#7F8C8D')
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=12,
                spaceBefore=20,
                textColor=colors.HexColor('#2C3E50')
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=6,
                alignment=TA_JUSTIFY
            )
            
            # Build document content
            story = []
            
            # Header
            story.append(Paragraph("SmartEvent AI Saathi", title_style))
            story.append(Paragraph("Professional Event Planning Summary", subtitle_style))
            story.append(Spacer(1, 20))
            
            # Event Overview
            story.append(Paragraph("Event Overview", heading_style))
            
            overview_text = f"""
            This comprehensive summary outlines the planning details for a {event_details['event_type'].lower()} 
            designed for {event_details['guest_count']} guests. The consultation has been structured to ensure 
            all aspects are covered within the specified requirements and budget considerations.
            """
            story.append(Paragraph(overview_text, normal_style))
            story.append(Spacer(1, 15))
            
            # Event Details Table
            story.append(Paragraph("Event Details", heading_style))
            
            details_data = [
                ['Event Type', event_details['event_type']],
                ['Guest Count', f"{event_details['guest_count']} people" if event_details['guest_count'] > 0 else "To be determined"],
                ['Venue', event_details['venue']],
                ['Location', event_details['city']],
                ['Cuisine', event_details['cuisine']],
                ['Date', event_details['date']],
                ['Budget', f"₹{event_details['budget']:,}" if event_details['budget'] > 0 else "To be finalized"]
            ]
            
            details_table = Table(details_data, colWidths=[4*cm, 10*cm])
            details_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#4ECDC4')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#000000')),  # Force black color
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),  # Make values bold
                ('FONTSIZE', (0, 0), (-1, -1), 11),  # Slightly larger font
                ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.white]),  # White background for values
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E9ECEF')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            
            story.append(details_table)
            story.append(Spacer(1, 20))
            
            # Budget Analysis (if budget is available)
            if event_details['budget'] > 0:
                budget_breakdown, total_budget = self.generate_budget_breakdown(
                    event_details['event_type'], 
                    event_details['budget'], 
                    event_details['guest_count']
                )
                
                story.append(Paragraph("Budget Analysis", heading_style))
                
                # Budget table
                budget_data = [['Category', 'Amount (₹)', '% of Total']]
                total_amount = 0
                
                for category, details in budget_breakdown.items():
                    amount = details['amount']
                    percentage = details['percentage']
                    budget_data.append([category, f"₹{amount:,}", f"{percentage}%"])
                    total_amount += amount
                
                budget_data.append(['Total', f"₹{total_amount:,}", "100%"])
                
                budget_table = Table(budget_data, colWidths=[6*cm, 4*cm, 3*cm])
                budget_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4ECDC4')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F8F9FA')]),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E9ECEF')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E9ECEF'))
                ]))
                
                story.append(budget_table)
                story.append(Spacer(1, 15))
                
                # Key Insights
                story.append(Paragraph("Key Insights", heading_style))
                
                cost_per_guest = total_budget // event_details['guest_count'] if event_details['guest_count'] > 0 else 0
                largest_category = max(budget_breakdown.items(), key=lambda x: x[1]['amount'])
                
                insights = [
                    f"• Cost per guest: ₹{cost_per_guest:,} per person",
                    f"• Largest expense: {largest_category[0]} ({largest_category[1]['percentage']}% of total budget)",
                    f"• Budget efficiency: Well-distributed across essential categories",
                    f"• Recommendation: Consider booking vendors early to secure better rates"
                ]
                
                for insight in insights:
                    story.append(Paragraph(insight, normal_style))
            
            # Vendor Selections (if any)
            if event_details.get('vendors'):
                story.append(Spacer(1, 15))
                story.append(Paragraph("Selected Vendors", heading_style))
                
                vendor_data = [['Service Type', 'Vendor Name']]
                for vendor in event_details['vendors']:
                    if 'catering' in vendor.lower():
                        vendor_data.append(['Catering', vendor])
                    elif 'decoration' in vendor.lower() or 'occasion' in vendor.lower():
                        vendor_data.append(['Decoration', vendor])
                    elif 'hotel' in vendor.lower():
                        vendor_data.append(['Venue', vendor])
                    else:
                        vendor_data.append(['Service', vendor])
                
                if len(vendor_data) > 1:  # Only create table if there are vendors
                    vendor_table = Table(vendor_data, colWidths=[6*cm, 8*cm])
                    vendor_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4ECDC4')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E9ECEF'))
                    ]))
                    story.append(vendor_table)
            
            # Key Requirements (if any)
            if event_details.get('requirements'):
                story.append(Spacer(1, 15))
                story.append(Paragraph("Key Requirements", heading_style))
                
                # Filter and clean requirements
                clean_requirements = []
                for req in event_details['requirements'][:5]:  # Limit to 5 requirements
                    req_clean = req.strip()
                    if len(req_clean) > 10 and req_clean not in clean_requirements:
                        clean_requirements.append(req_clean)
                
                for req in clean_requirements:
                    story.append(Paragraph(f"• {req}", normal_style))
            
            # Footer
            story.append(Spacer(1, 30))
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=9,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#7F8C8D')
            )
            
            story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", footer_style))
            story.append(Paragraph("SmartEvent AI Saathi - Professional Event Planning Assistant", footer_style))
            
            # Build PDF
            doc.build(story)
            
            return str(filepath)
            
        except Exception as e:
            print(f"PDF generation error: {e}")
            # Fallback to HTML
            return self.generate_summary_html(event_details, conversation_id)
    
    def generate_summary_html(self, event_details: Dict, conversation_id: str) -> str:
        """Generate HTML summary document"""
        budget_breakdown, total_budget = self.generate_budget_breakdown(
            event_details["event_type"], 
            event_details["budget"], 
            event_details["guest_count"]
        )
        
        chart_base64 = self.create_budget_chart(budget_breakdown)
        
        # Calculate per person cost
        per_person_cost = total_budget // event_details["guest_count"] if event_details["guest_count"] > 0 else 0
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Event Planning Summary</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    background-color: #f8f9fa;
                    color: #333;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    border-bottom: 3px solid #4ECDC4;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    color: #2C3E50;
                    margin: 0;
                    font-size: 28px;
                }}
                .header p {{
                    color: #7F8C8D;
                    margin: 5px 0;
                }}
                .section {{
                    margin-bottom: 25px;
                }}
                .section h2 {{
                    color: #2C3E50;
                    border-left: 4px solid #4ECDC4;
                    padding-left: 15px;
                    margin-bottom: 15px;
                }}
                .overview {{
                    background: #ECF0F1;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }}
                .details-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    margin-bottom: 20px;
                }}
                .detail-card {{
                    background: #F8F9FA;
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 4px solid #4ECDC4;
                }}
                .detail-card h3 {{
                    margin: 0 0 10px 0;
                    color: #2C3E50;
                }}
                .detail-card p {{
                    margin: 0;
                    font-size: 16px;
                    font-weight: 500;
                }}
                .budget-section {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 30px;
                    align-items: start;
                }}
                .budget-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                }}
                .budget-table th, .budget-table td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                .budget-table th {{
                    background-color: #4ECDC4;
                    color: white;
                    font-weight: 600;
                }}
                .budget-table tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                .total-row {{
                    font-weight: bold;
                    background-color: #E8F6F3 !important;
                }}
                .chart-container {{
                    text-align: center;
                }}
                .chart-container img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 8px;
                }}
                .insights {{
                    background: #E8F6F3;
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 4px solid #27AE60;
                }}
                .insights ul {{
                    margin: 0;
                    padding-left: 20px;
                }}
                .insights li {{
                    margin-bottom: 8px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    color: #7F8C8D;
                }}
                @media print {{
                    body {{ background: white; }}
                    .container {{ box-shadow: none; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{event_details["event_type"]} Planning Summary</h1>
                    <p>Generated on {datetime.now().strftime("%B %d, %Y")}</p>
                    <p>SmartEvent AI Saathi - AI Event Planning Assistant</p>
                </div>
                
                <div class="section">
                    <div class="overview">
                        <h2>Event Overview</h2>
                        <p>This comprehensive summary outlines the planning details for a {event_details["event_type"].lower()} 
                        designed for {event_details["guest_count"]} guests. The event planning process has been carefully 
                        structured to ensure all aspects are covered within the specified budget and requirements.</p>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Event Details</h2>
                    <div class="details-grid">
                        <div class="detail-card">
                            <h3>Event Type</h3>
                            <p>{event_details["event_type"]}</p>
                        </div>
                        <div class="detail-card">
                            <h3>Guest Count</h3>
                            <p>{event_details["guest_count"]} people</p>
                        </div>
                        <div class="detail-card">
                            <h3>Venue</h3>
                            <p>{event_details["venue"]}</p>
                        </div>
                        <div class="detail-card">
                            <h3>Total Budget</h3>
                            <p>Rupees {total_budget:,}</p>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Budget Analysis</h2>
                    <div class="budget-section">
                        <div>
                            <table class="budget-table">
                                <thead>
                                    <tr>
                                        <th>Category</th>
                                        <th>Amount (Rupees)</th>
                                        <th>% of Total</th>
                                    </tr>
                                </thead>
                                <tbody>
        """
        
        # Add budget breakdown rows
        for category, details in budget_breakdown.items():
            html_content += f"""
                                    <tr>
                                        <td>{category}</td>
                                        <td>{details["amount"]:,}</td>
                                        <td>{details["percentage"]}%</td>
                                    </tr>
            """
        
        html_content += f"""
                                    <tr class="total-row">
                                        <td><strong>Total</strong></td>
                                        <td><strong>Rupees {total_budget:,}</strong></td>
                                        <td><strong>100%</strong></td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <div class="chart-container">
        """
        
        if chart_base64:
            html_content += f'<img src="data:image/png;base64,{chart_base64}" alt="Budget Distribution Chart">'
        else:
            html_content += '<p>Budget visualization not available</p>'
        
        html_content += f"""
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <div class="insights">
                        <h2>Key Insights</h2>
                        <ul>
                            <li><strong>Cost per guest:</strong> Rupees {per_person_cost:,} per person</li>
                            <li><strong>Largest expense:</strong> {max(budget_breakdown.keys(), key=lambda x: budget_breakdown[x]["amount"])} 
                                ({max(budget_breakdown.values(), key=lambda x: x["amount"])["percentage"]}% of total budget)</li>
                            <li><strong>Budget efficiency:</strong> Well-distributed across essential categories</li>
                            <li><strong>Recommendation:</strong> Consider booking vendors early to secure better rates</li>
                        </ul>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Document ID: {conversation_id}</p>
                    <p>This summary was generated by SmartEvent AI Saathi based on your conversation.</p>
                    <p>For questions or modifications, please contact your event planning assistant.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def save_summary(self, conversation_data: Dict, format_type: str = "pdf") -> Dict:
        """Generate and save event summary in PDF or HTML format"""
        try:
            # Extract conversation details
            conversation_history = conversation_data.get("conversation_history", [])
            agent_id = conversation_data.get("agent_id", "unknown")
            
            # Extract event details from conversation
            event_details = self.extract_event_details_from_conversation(conversation_history)
            
            # Generate summary based on format
            if format_type.lower() == "pdf" and DEPENDENCIES_AVAILABLE:
                filepath = self.generate_summary_pdf(event_details, agent_id)
                filename = Path(filepath).name
                url = f"/summary/download/{filename}"
            else:
                # Fallback to HTML
                html_content = self.generate_summary_html(event_details, agent_id)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"event_summary_{agent_id}_{timestamp}.html"
                filepath = self.output_dir / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                url = f"/summary/view/{filename}"
            
            return {
                "success": True,
                "filename": filename,
                "filepath": str(filepath),
                "event_details": event_details,
                "url": url,
                "format": "pdf" if str(filepath).endswith('.pdf') else "html"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Global instance
summary_generator = EventSummaryGenerator()

def generate_event_summary(conversation_data: Dict) -> Dict:
    """Generate event summary from conversation data"""
    return summary_generator.save_summary(conversation_data)