#!/usr/bin/python
import cgi, cgitb, sys, traceback, string
cgitb.enable()

print "Content-type: text/html\n"
import os, codecs, re
import time

DEBUG_TEXT = ""
def debugPrint(s):
	global DEBUG_TEXT
	DEBUG_TEXT = DEBUG_TEXT + str(s) + "\n"

# read a unicode file
def readfile(filename):
	handle = codecs.open(filename)
	return handle.read()

# replace ${} tags with dictionary values or empty string
def fill(text, values):
	instances = re.findall("\$\{\w*\}", text)
	if instances and len(instances) > 0:
		for key in instances:
			unwrapped = key[2:-1]

			if unwrapped in values:
				text = text.replace(key, str(values[unwrapped]))
			else:
				text = text.replace(key, '')
	return text

# main layout as stored in html
PAGE = readfile("page.html")

# /error/code page and internal errors
ERROR_FORMAT = """
<!-- WEBSITE ERROR -->
<div id="blog">
    <div class="pre-article">
        <!-- title -->
        <h3>Page Error</h3>
        ${error}
    </div>
    <div class="main-article">
        ${details}
    </div>
</div>
"""

# blog post page format
BLOG_FORMAT = """
<!-- 
WEBSITE PAGE ${id}
${title}
${summary}
${image}
${thumb}
${date} - ${timestamp}
${product}
 -->
<div id="blog">
    <div class="pre-article">
        <!-- title -->
        <h2>${title}</h2>
        ${info}
    </div>
    <div class="main-article">
        ${content}
    </div>
    <span class="post-article">
        Posted by Greg on ${timestamp}
    </span>
</div>
"""

# directory listing format - entry
LISTING_ENTRY = """
<a href="/?"></a><br>
"""

# directory listing format
LISTING_FORMAT = """
	<h2>Directory listing</h2>
	<p>
		${entries}
	</p>
"""

# home page format - entry
HOME_PAGE_ENTRY = """
		<div class="home-entry">
		  <a href="/post/${id}" class="link"><h4>${title}</h4></a>
		  <span class="price">${price}</span>
		  <p>
		    <img class="home-thumb" src="/images/${thumb}"><br>
		    ${summary}
		  </p>
		</div>
"""

# home page format
HOME_FORMAT = """
<div id="homepage">
	<h1>Home Page</h1>
	<p>
		${entries}
	</p>
	<a href="/home/${previous}"><< prev</a> &nbsp;&nbsp; ${pagenum} &nbsp;&nbsp; <a href="/home/${next}">next >></a>
</div>
"""

# parse a post file
ARTICLES = dict()
def parsedata(textdata, id = 0):
	global ARTICLES
	data = dict([('id', id)])
	lines = textdata.splitlines()
	linenum = 0
	# parse each line
	while linenum < len(lines):
		linetext = lines[linenum]
		idx = linetext.find(':')
		if idx >= 0:
			entry, value = linetext.split(':')
			if entry != 'content':
				data[entry] = value
			else:
				break
		linenum = linenum + 1
	# condense the rest into the content tag
	data['content'] = '\n'.join(lines[linenum+1:])
	# format the date
	data['timestamp'] = "this day last week"
	if 'date' in data:
		stamp = time.strptime(data['date'], "%m-%d-%Y")
		if stamp:
			data['timestamp'] = time.strftime("%B %d, %Y", stamp)
	# store the post in the lookup table
	ARTICLES[id] = data
	return data

# load all posts
def loadposts():
	posts = []
	for root, dirs, files in os.walk('posts'):
		for filename in files:
			if filename.endswith('.txt'):
				match = re.search("post([0-9]+)", filename)
				if match:
					idnum = int(match.group(1))
					filepath = os.path.join(root, filename)
					text = readfile(filepath)
					post = parsedata(text, idnum)
					posts.append(post)
	return posts



# insert into ${main_content}
def display(content):
	print fill(PAGE, {'main_content': content})

# error page
def displayError(errorcode = "Error."):
	message = cgi.escape(errorcode)
	details = 'Return home: <a href="//gregbuildscomputers.com">gregbuildscomputers.com</a>'
	values = dict([('error', message), ('details', details)])
	content = fill(ERROR_FORMAT, values)
	display(content)

# display a list of posts and listings
def displayListing(param):
	display(LISTING_FORMAT)

# display a specific post or listing
def displayPost(postStr):
	postNum = -1
	try:
		postNum = int(postStr)
	except:
		postNum = -1

	if postNum >= 0 and postNum in ARTICLES:
		post = ARTICLES[postNum]
		content = fill(BLOG_FORMAT, post)
		display(content)
	else:
		displayError("Can't find post.")

# display the home page
def displayHome():
	entries = ""
	posts = postdata[0:10]
	for post in posts:
		entry = fill(HOME_PAGE_ENTRY, post)
		entries = entries + entry
	content = fill(HOME_FORMAT, {'entries': entries, 'previous': 0, 'pagenum': 1, 'next': 2})
	display(content)

# parse params and load site data
arguments = cgi.FieldStorage()
postdata = loadposts()

# decide which page to load
if 'post' in arguments:
	displayPost(arguments['post'].value)
elif 'listing' in arguments:
	displayListing(arguments['listing'].value)
elif 'error' in arguments:
	try:
		value = int(arguments['error'].value)
	except:
		value = -1
	displayError(str(value))
else:
	displayHome()

debugPrint("Loaded " + str(len(postdata)) + " posts.")
print "<!-- \n" + DEBUG_TEXT + " -->"
