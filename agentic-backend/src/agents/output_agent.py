"""
Output Agent - Step 8: Assemble final report and generate PDF
"""
from typing import Dict
from datetime import datetime
from pathlib import Path
import os


class OutputAgent:
    """Step 8: Generate Report Output with PDF"""
    
    async def execute(self, state_data: Dict) -> Dict:
        """Assemble all sections into final report and generate PDF"""
        try:
            client_name = state_data.get("client_name", "Client")
            period = state_data.get("period", {})
            firm_name = state_data.get("firm_name", "Wealth Management Firm")
            
            section_results = state_data.get("section_results", {})
            
            # Assemble report structure
            report = {
                'cover_page': {
                    'client_name': client_name,
                    'period': period['name'],
                    'firm_name': firm_name,
                    'generation_date': datetime.now().strftime("%B %d, %Y"),
                    'report_title': f"Portfolio Performance Report - {period['name']}"
                },
                'sections': section_results,
                'total_sections': len(section_results)
            }
            
            # Generate PDF
            pdf_path = await self._generate_pdf(report, client_name, period['name'])
            
            # Generate summary
            summary = self._generate_summary(section_results)
            
            return {
                "status": "complete",
                "section": "output",
                "report": report,
                "summary": summary,
                "pdf_path": pdf_path,
                "message": f"Complete report generated for {client_name} - {period['name']}",
                "pdf_ready": True
            }
            
        except Exception as e:
            import traceback
            return {
                "status": "error",
                "error": f"{str(e)}\n{traceback.format_exc()}"
            }
    
    async def _generate_pdf(self, report: Dict, client_name: str, period: str) -> str:
        """Generate PDF report using reportlab"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib import colors
            
            # Create output directory
            output_dir = Path(__file__).parent.parent.parent.parent / "output" / "reports"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{client_name.replace(' ', '_')}_{period.replace(' ', '_')}_{timestamp}.pdf"
            pdf_path = output_dir / filename
            
            # Create PDF
            doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=30,
                alignment=1  # Center
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=12
            )
            
            # Cover Page
            story.append(Spacer(1, 2*inch))
            story.append(Paragraph(report['cover_page']['firm_name'], title_style))
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph(report['cover_page']['report_title'], styles['Heading2']))
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph(f"Prepared for: {report['cover_page']['client_name']}", styles['Normal']))
            story.append(Paragraph(f"Report Date: {report['cover_page']['generation_date']}", styles['Normal']))
            story.append(PageBreak())
            
            sections = report['sections']
            
            # Performance Summary
            if 'performance_summary' in sections:
                perf = sections['performance_summary']
                story.append(Paragraph("Performance Summary", heading_style))
                story.append(Spacer(1, 0.2*inch))
                
                # Performance table
                if 'performance_table' in perf:
                    pt = perf['performance_table']
                    data = [['Period'] + pt['periods']]
                    data.append(['Portfolio'] + [f"{v:.2f}%" if v else "N/A" for v in pt['portfolio']])
                    data.append(['Benchmark'] + [f"{v:.2f}%" if v else "N/A" for v in pt['benchmark']])
                    data.append(['Difference'] + [f"{v:+.2f}%" if v else "N/A" for v in pt['difference']])
                    
                    table = Table(data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(table)
                    story.append(Spacer(1, 0.3*inch))
                
                if 'narrative' in perf:
                    story.append(Paragraph(perf['narrative'], styles['Normal']))
                
                story.append(PageBreak())
            
            # Allocation Overview
            if 'allocation_overview' in sections:
                alloc = sections['allocation_overview']
                story.append(Paragraph("Allocation Overview", heading_style))
                story.append(Spacer(1, 0.2*inch))
                
                if 'allocation_table' in alloc:
                    data = [['Asset Class', '% of Portfolio', 'Value']]
                    for item in alloc['allocation_table']:
                        data.append([
                            item['asset_class'],
                            f"{item['percentage']:.1f}%",
                            f"${item['value']:,.0f}"
                        ])
                    
                    table = Table(data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(table)
                
                story.append(PageBreak())
            
            # Holdings Detail
            if 'holdings_detail' in sections:
                holdings = sections['holdings_detail']
                story.append(Paragraph("Holdings Detail", heading_style))
                story.append(Spacer(1, 0.2*inch))
                
                if 'holdings_table' in holdings:
                    data = [['Security', 'Shares', 'Price', 'Value', '% Port', 'QTD Return']]
                    for h in holdings['holdings_table'][:10]:  # Top 10
                        data.append([
                            h['security'],
                            f"{h['shares']:.0f}",
                            f"${h['price']:.2f}",
                            f"${h['value']:,.0f}",
                            f"{h['percentage']:.1f}%",
                            f"{h['qtd_return']:+.2f}%"
                        ])
                    
                    table = Table(data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(table)
                
                story.append(PageBreak())
            
            # Market Commentary
            if 'market_commentary' in sections:
                comm = sections['market_commentary']
                story.append(Paragraph("Market Commentary", heading_style))
                story.append(Spacer(1, 0.2*inch))
                
                if 'market_summary' in comm:
                    story.append(Paragraph("<b>Market Summary:</b>", styles['Normal']))
                    story.append(Paragraph(comm['market_summary'], styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))
                
                if 'portfolio_impact' in comm:
                    story.append(Paragraph("<b>Portfolio Impact:</b>", styles['Normal']))
                    story.append(Paragraph(comm['portfolio_impact'], styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))
                
                if 'outlook' in comm:
                    story.append(Paragraph("<b>Outlook:</b>", styles['Normal']))
                    story.append(Paragraph(comm['outlook'], styles['Normal']))
                
                story.append(PageBreak())
            
            # Planning Notes
            if 'planning_notes' in sections:
                planning = sections['planning_notes']
                story.append(Paragraph("Planning Notes", heading_style))
                story.append(Spacer(1, 0.2*inch))
                
                if 'recommendations' in planning:
                    story.append(Paragraph("<b>Recommendations:</b>", styles['Normal']))
                    story.append(Paragraph(planning['recommendations'], styles['Normal']))
                    story.append(Spacer(1, 0.2*inch))
                
                if 'action_items' in planning:
                    story.append(Paragraph("<b>Action Items:</b>", styles['Normal']))
                    for item in planning['action_items']:
                        story.append(Paragraph(f"• {item}", styles['Normal']))
                
                story.append(PageBreak())
            
            # Disclosures
            story.append(Paragraph("Disclosures", heading_style))
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph(
                "Past performance does not guarantee future results. All investments carry risk of loss. "
                "This report is for informational purposes only and does not constitute investment advice.",
                styles['Normal']
            ))
            
            # Build PDF
            doc.build(story)
            
            return str(pdf_path.absolute())
            
        except ImportError:
            # reportlab not installed
            return "PDF generation requires reportlab: pip install reportlab"
        except Exception as e:
            return f"PDF generation failed: {str(e)}"
    
    def _generate_summary(self, sections: Dict) -> str:
        """Generate executive summary"""
        completed = len(sections)
        section_names = list(sections.keys())
        return f"Report complete with {completed} sections: {', '.join(section_names)}"
