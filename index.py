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

HOME_FORMAT = """


"""

LISTING_ENTRY = """
<a href="/?"></a>
"""

LISTING_FORMAT = """
	<p>
		${entries}
	</p>
"""

# read a unicode file
def readfile(filename):
	handle = codecs.open(filename)
	return handle.read()

PAGE = readfile("page.html")

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
	data['timestamp'] = "recently"
	if 'date' in data:
		stamp = time.strptime(data['date'], "%m-%d-%Y")
		if stamp:
			data['timestamp'] = time.strftime("%B %d, %Y", stamp)
	# store the post in the lookup table
	debugPrint("Adding article to index " + str(id))
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

# replace ${} tags with dictionary values or empty string
def inject(text, values):
	instances = re.findall("\$\{\w*\}", text)
	if instances and len(instances) > 0:
		for key in instances:
			unwrapped = key[2:-1]

			if unwrapped in values:
				#debugPrint("Replacing '%s' with '%s'" % (key, str(values[unwrapped])))
				text = text.replace(key, str(values[unwrapped]))
			else:
				text = text.replace(key, '')
	return text

# insert into ${main_content}
def display(content):
	print inject(PAGE, {'main_content': content})

# error page
def displayError(message = "", details = ""):
	values = dict([('error', message), ('details', details)])
	content = inject(ERROR_FORMAT, values)
	display(content)

# display a list of posts and listings
def displayListing(param):
	display('Directory listing:')

# display a specific post or listing
def displayPost(postStr):
	postNum = -1
	try:
		postNum = int(postStr)
	except:
		postNum = -1

	debugPrint("Post string: '" + str(postStr) + "'")
	debugPrint("Post num: " + str(postNum))

	if postNum >= 0 and postNum in ARTICLES:
		post = ARTICLES[postNum]
		content = inject(BLOG_FORMAT, post)
		display(content)
	else:
		displayError("Can't find post.", 'Return home: <a href="http://gregbuildscomputers.com/">gregbuildscomputers.com</a>')

# display the home page
def displayHome():
	display("<h1>Homepage</h1>")

# parse params and load site data
arguments = cgi.FieldStorage()
postdata = loadposts()

# decide which page to load
if 'post' in arguments:
	displayPost(arguments['post'].value)
elif 'listing' in arguments:
	displayListing(arguments['listing'].value)
elif 'error' in arguments:
	details = ''
	if 'details' in arguments:
		details = arguments['details'].value
	displayError(arguments['error'].value, details)
else:
	displayHome()

print "<!-- \n" + DEBUG_TEXT + " -->"
