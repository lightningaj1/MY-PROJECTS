"""
Learning Module - Geology and Mineral Education Content Management
Handles public learning pages and admin content management
"""

from flask import render_template, request, jsonify, redirect, session
from app.db import get_db
from app.helpers import login_required
from app.utils import is_admin

def learning_routes(app):
    """Register learning/education routes"""
    
    # ============================================================
    # PUBLIC LEARNING PAGES
    # ============================================================
    
    @app.route("/learn")
    def learn_home():
        """Main learning page with all lessons"""
        db = get_db()
        
        # Get all lessons grouped by category
        lessons = db.execute("""
            SELECT id, title, category, summary, image, difficulty_level, created_at
            FROM learning_content
            ORDER BY category, created_at DESC
        """).fetchall()
        lessons = [dict(l) for l in lessons]
        
        # Get categories for filter dropdown
        categories = db.execute("""
            SELECT DISTINCT category 
            FROM learning_content 
            ORDER BY category
        """).fetchall()
        categories = [cat['category'] for cat in categories]
        
        return render_template("learn.html", lessons=lessons, categories=categories)
    
    @app.route("/learn/<int:lesson_id>")
    def learn_detail(lesson_id):
        """View individual lesson detail"""
        db = get_db()
        
        # Get lesson
        lesson = db.execute("""
            SELECT * FROM learning_content WHERE id = ?
        """, (lesson_id,)).fetchone()
        
        if not lesson:
            return redirect("/learn")
        
        lesson = dict(lesson)
        
        # Parse related minerals
        related_minerals = []
        if lesson.get('related_minerals'):
            mineral_names = lesson['related_minerals'].split(',')
            related_minerals = db.execute("""
                SELECT id, name, formula, image FROM minerals 
                WHERE name IN ({})
                ORDER BY name
            """.format(','.join('?' * len(mineral_names))), mineral_names).fetchall()
            related_minerals = [dict(m) for m in related_minerals]
        
        # Get related lessons (same category, different lesson)
        related_lessons = db.execute("""
            SELECT id, title, category, summary, difficulty_level
            FROM learning_content
            WHERE category = ? AND id != ?
            LIMIT 3
        """, (lesson['category'], lesson_id)).fetchall()
        related_lessons = [dict(l) for l in related_lessons]
        
        return render_template("learn_detail.html", 
                             lesson=lesson, 
                             related_minerals=related_minerals,
                             related_lessons=related_lessons)
    
    # ============================================================
    # ADMIN LEARNING MANAGEMENT
    # ============================================================
    
    @app.route("/admin/learning")
    @login_required
    def manage_learning():
        """Admin page to manage all learning content"""
        if not is_admin():
            return redirect("/")
        
        db = get_db()
        
        # Get all lessons with stats
        lessons = db.execute("""
            SELECT id, title, category, summary, difficulty_level, created_at
            FROM learning_content
            ORDER BY created_at DESC
        """).fetchall()
        lessons = [dict(l) for l in lessons]
        
        # Count by category
        category_stats = db.execute("""
            SELECT category, COUNT(*) as count 
            FROM learning_content 
            GROUP BY category
        """).fetchall()
        category_stats = {cat['category']: cat['count'] for cat in category_stats}
        
        # Difficulty level stats
        difficulty_stats = db.execute("""
            SELECT difficulty_level, COUNT(*) as count 
            FROM learning_content 
            GROUP BY difficulty_level
        """).fetchall()
        difficulty_stats = {d['difficulty_level']: d['count'] for d in difficulty_stats}
        
        return render_template("admin_learning.html", 
                             lessons=lessons,
                             category_stats=category_stats,
                             difficulty_stats=difficulty_stats)
    
    @app.route("/admin/learning/add", methods=["GET", "POST"])
    @login_required
    def add_learning():
        """Add new learning content"""
        if not is_admin():
            return redirect("/")
        
        db = get_db()
        
        if request.method == "POST":
            title = request.form.get("title")
            category = request.form.get("category")
            summary = request.form.get("summary")
            content = request.form.get("content")
            image = request.form.get("image", "/static/images/default_lesson.jpg")
            difficulty_level = request.form.get("difficulty_level", "beginner")
            related_minerals = request.form.get("related_minerals", "")
            
            errors = []
            if not title:
                errors.append("Title is required")
            if not category:
                errors.append("Category is required")
            if not content:
                errors.append("Content is required")
            if not summary:
                errors.append("Summary is required")
            
            if errors:
                # Get available minerals for dropdown
                minerals = db.execute("""
                    SELECT id, name FROM minerals ORDER BY name
                """).fetchall()
                minerals = [dict(m) for m in minerals]
                
                return render_template("admin_learning_form.html",
                                     errors=errors,
                                     minerals=minerals,
                                     form_data=request.form)
            
            # Clean up related minerals (remove whitespace)
            related_minerals = ','.join([m.strip() for m in related_minerals.split(',') if m.strip()])
            
            db.execute("""
                INSERT INTO learning_content (created_by, title, category, summary, content, image, difficulty_level, related_minerals)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (session.get('user_id'), title, category, summary, content, image, difficulty_level, related_minerals))
            
            db.commit()
            return redirect("/admin/learning")
        
        # GET request - show form
        minerals = db.execute("""
            SELECT id, name FROM minerals ORDER BY name
        """).fetchall()
        minerals = [dict(m) for m in minerals]
        
        return render_template("admin_learning_form.html", minerals=minerals)
    
    @app.route("/admin/learning/<int:lesson_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_learning(lesson_id):
        """Edit learning content"""
        if not is_admin():
            return redirect("/")
        
        db = get_db()
        lesson = db.execute("""
            SELECT * FROM learning_content WHERE id = ?
        """, (lesson_id,)).fetchone()
        
        if not lesson:
            return redirect("/admin/learning")
        
        lesson = dict(lesson)
        
        if request.method == "POST":
            title = request.form.get("title")
            category = request.form.get("category")
            summary = request.form.get("summary")
            content = request.form.get("content")
            image = request.form.get("image", lesson['image'])
            difficulty_level = request.form.get("difficulty_level", "beginner")
            related_minerals = request.form.get("related_minerals", "")
            
            errors = []
            if not title:
                errors.append("Title is required")
            if not category:
                errors.append("Category is required")
            if not content:
                errors.append("Content is required")
            if not summary:
                errors.append("Summary is required")
            
            if errors:
                minerals = db.execute("""
                    SELECT id, name FROM minerals ORDER BY name
                """).fetchall()
                minerals = [dict(m) for m in minerals]
                
                form_data = {
                    'title': title,
                    'category': category,
                    'summary': summary,
                    'content': content,
                    'image': image,
                    'difficulty_level': difficulty_level,
                    'related_minerals': related_minerals
                }
                
                return render_template("admin_learning_form.html",
                                     lesson=lesson,
                                     errors=errors,
                                     minerals=minerals,
                                     form_data=form_data)
            
            # Clean up related minerals
            related_minerals = ','.join([m.strip() for m in related_minerals.split(',') if m.strip()])
            
            db.execute("""
                UPDATE learning_content 
                SET title = ?, category = ?, summary = ?, content = ?, 
                    image = ?, difficulty_level = ?, related_minerals = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (title, category, summary, content, image, difficulty_level, related_minerals, lesson_id))
            
            db.commit()
            return redirect("/admin/learning")
        
        # GET request - show form with current data
        minerals = db.execute("""
            SELECT id, name FROM minerals ORDER BY name
        """).fetchall()
        minerals = [dict(m) for m in minerals]
        
        return render_template("admin_learning_form.html", 
                             lesson=lesson,
                             minerals=minerals)
    
    @app.route("/admin/learning/<int:lesson_id>/delete", methods=["POST"])
    @login_required
    def delete_learning(lesson_id):
        """Delete learning content"""
        if not is_admin():
            return jsonify({'error': 'Not authorized'}), 403
        
        db = get_db()
        
        # Check if lesson exists
        lesson = db.execute("""
            SELECT id FROM learning_content WHERE id = ?
        """, (lesson_id,)).fetchone()
        
        if not lesson:
            return jsonify({'error': 'Lesson not found'}), 404
        
        db.execute("DELETE FROM learning_content WHERE id = ?", (lesson_id,))
        db.commit()
        
        return jsonify({'success': True})
    
    # ============================================================
    # API ENDPOINTS
    # ============================================================
    
    @app.route("/api/learning/categories")
    def get_learning_categories():
        """Get all lesson categories"""
        db = get_db()
        
        categories = db.execute("""
            SELECT DISTINCT category 
            FROM learning_content 
            ORDER BY category
        """).fetchall()
        
        return jsonify([cat['category'] for cat in categories])
    
    @app.route("/api/learning/by-mineral/<mineral_name>")
    def get_learning_by_mineral(mineral_name):
        """Get lessons related to a specific mineral"""
        db = get_db()
        
        lessons = db.execute("""
            SELECT id, title, category, summary, difficulty_level
            FROM learning_content
            WHERE related_minerals LIKE ?
            LIMIT 5
        """, (f'%{mineral_name}%',)).fetchall()
        
        return jsonify([dict(l) for l in lessons])
    
    @app.route("/api/learning/summary")
    def get_learning_summary():
        """Get summary statistics for learning content"""
        db = get_db()
        
        total = db.execute("SELECT COUNT(*) as count FROM learning_content").fetchone()['count']
        
        categories = db.execute("""
            SELECT COUNT(DISTINCT category) as count FROM learning_content
        """).fetchone()['count']
        
        by_difficulty = db.execute("""
            SELECT difficulty_level, COUNT(*) as count 
            FROM learning_content 
            GROUP BY difficulty_level
        """).fetchall()
        
        return jsonify({
            'total_lessons': total,
            'total_categories': categories,
            'by_difficulty': {d['difficulty_level']: d['count'] for d in by_difficulty}
        })
