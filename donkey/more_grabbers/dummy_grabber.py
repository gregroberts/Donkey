#This file shows the structure required for a grabber.
#each grabber must implement a method called 'grabber'
#this method takes a dictionary of parameters and returns some kind of result
#what the hell else you include is up to you.
#each grabber must also have an 'info' object.
#this is used to document the grabber, and to construct the help info


def grabber(k):
	'''this is the entry point of the grabber.
		this receives all the parameters you send in the 'fetch' command
		and returns your data
	'''
	return ''


#this is essentially the documentation for the grabber
info = {
	#an informative name!
	'name':'',
	#a brief outline of what it does
	'short_description':'',
	#a longer explanation of what it does and how it can be used
	'long_description':'',
	#the kwargs which MUST be present for a successful grab
	'required_parameters':{
		#document what each kwarg means
		'kwarg_name':'kwarg_description'
	}
	#optional parameter list doesn't have to be exhaustive.
	#some grabbers may be very flexible. The scope of usage should be outlined in long_description
	#use this entry for parameters which *may* be present on any fetch request, but which aren't obligatory
	'optional_parameters':{
		#document what each kwarg means
		'kwarg_name':'kwarg_description'
	},
	#if your grabber wraps an API or something, link to it here.
	#if there's some page which will help to use the thing, link it, dummy!
	'url':''
}