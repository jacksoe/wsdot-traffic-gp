'''travelerinfo
Returns data from the WSDOT Traveler Info REST endpoints.
@author: Jeff Jacobson

Parameters:
1	data name
2	WSDOT Traffic API access code (optional if default is set via WSDOT_TRAFFIC_API_CODE environment variable or accesscode.txt file.)
'''
import sys, os, urllib2, json, parseutils, json
from resturls import urls

# Get default access code
default_access_code = None
fn = "accesscode.txt"
envvarname = "WSDOT_TRAFFIC_API_CODE"
if os.path.exists(fn):
	with open(fn, "r") as f:
		default_access_code = f.read()
else:
	if envvarname in os.environ:
		default_access_code = os.environ[envvarname]

_no_code_msg = "No access code provided. Must be provided either by parameter or WSDOT_TRAFFIC_API_CODE enviroment variable."

def parseTravelerInfoObject(dct):
	"""This method is used by the json.load method to customize how the alerts are deserialized.
	@type dct: dict
	@return: dictionary with flattened JSON output
	@rtype: dict
	"""
	output = {}
	for key, val in dct.iteritems():
		if isinstance(val, dict):
			# Roadway locations will be "flattened", since tables can't have nested values.
			for rlKey in val:
				output[key + rlKey] = val[rlKey]
		elif key == "LocationID":
			output[key] = "{%s}" % val
		elif isinstance(val, (str, unicode)):
			# Parse date/time values.
			output[key] = parseutils.parseDate(val) # Either parses into date (if possible) or returns the original string.
		else:
			output[key] = dct[key]
	return output

def getTravelerInfoJson(dataname, accesscode=default_access_code):
	"""Gets the highway alerts data from the REST endpoint.
	@param dataname: The name of the traffic data set to retrieve.
	@type dataname: str
	@param accesscode: Access code. (optional if default is provided.)
	@type accesscode: str
	@return: The JSON output from the rest endpoint
	@rtype: list
	"""
	if not accesscode:
		raise TypeError(_no_code_msg)
	url = "%s?AccessCode=%s" % (urls[dataname], accesscode)
	f = urllib2.urlopen(url)
	output = f.read()
	del f
	return output

def getTravelerInfo(dataname, accesscode=default_access_code):
	"""Gets the highway alerts data from the REST endpoint.
	@param dataname: The name of the traffic data set to retrieve.
	@type dataname: str
	@param accesscode: Access code. (optional if default is provided.)
	@type accesscode: str
	@return: Returns a list of dict objects.
	@rtype: list
	"""
	if not accesscode:
		raise TypeError(_no_code_msg)
	url = "%s?AccessCode=%s" % (urls[dataname], accesscode)
	f = urllib2.urlopen(url)
	jsonData = json.load(f, object_hook=parseTravelerInfoObject)
	del f
	return jsonData


if __name__ == '__main__':
	if len(sys.argv) < 2:
		# Create list of valid values for error message.
		valid_keys = list(urls.keys())
		valid_keys.sort()
		sys.stderr.write("You must provide the traffic api type as a parameter. Valid values are:\n")
		for k in valid_keys:
			sys.stderr.write("\t%s\n" % k)
		exit(1)
	elif len(sys.argv) < 3 and default_access_code is None:
		sys.exit("No access code was provided")
	else:
		name = sys.argv[1]
		code = default_access_code
		if len(sys.argv) >= 3:
			code = sys.argv[2]
		json.dump(getTravelerInfo(name, code), sys.stdout, indent=True)