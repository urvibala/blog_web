from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
import os
from wtforms import StringField, SubmitField, FileField, TextAreaField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename

# Configuration
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.secret_key = 'abc'
csrf = CSRFProtect(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# DatabaseConfiguration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blogs.db'
db = SQLAlchemy(app)

# Blog Model
class Blogs(db.Model):
    __tablename__ = 'blogs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(255), nullable=True)
    likes = db.Column(db.Integer, default=0)
    liked = db.Column(db.Boolean, default=False)

# Form Definitions
class BlogForm(FlaskForm):
    name = StringField("Author's name")
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    image = FileField('Image')
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    search = StringField('Search')
    submit = SubmitField('Submit')


# Create the database tables
with app.app_context():
    db.create_all()

# Home page
@app.route("/")
def home():
    blogs = db.session.execute(db.select(Blogs).order_by(Blogs.title))
    all_blogs = blogs.scalars()
    return render_template('home.html',
                           blogs=all_blogs)


# Function to check if a file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Add Blog Page
@app.route("/add", methods=["GET", "POST"])
def add():
    form = BlogForm()
    if request.method == "POST":
        # Create a new blog record
        new_blog = Blogs(
            name=form.name.data,
            title=form.title.data,
            content=form.content.data,
            image_path=save_image(request.files['image']),
        )
        db.session.add(new_blog)
        db.session.commit()
        flash('Blog successfully added!', 'success') 
        return redirect(url_for('home'))
    return render_template("add.html", form=form)

# Function to save an uploaded image
def save_image(image_file):
    # Generate a unique filename for the image
    filename = secure_filename(image_file.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Save the image to the specified path
    image_file.save(image_path)
    return filename

# View Blog Page
@app.route('/blog/<int:blog_id>')
def view_blog(blog_id):
    blog = Blogs.query.get_or_404(blog_id)
    return render_template('blog.html', blog=blog)


# Search page
@app.route('/search')
def search():
    form = SearchForm()
    query = request.args.get('search', '')

    if query:
        # Search for blogs that contain the query in name, title, or content
        results = Blogs.query.filter(Blogs.name.contains(query) | Blogs.title.contains(query) | Blogs.content.contains(query)).all()
    else:
        results = []
    return render_template('search.html', form=form, results=results)


if __name__ == '__main__':
    app.run(debug=True)

