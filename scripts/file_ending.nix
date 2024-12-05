

''
# get only the ending of a file
function file_ending {
	echo $1 | sed 's/^.*\.//'
}
''