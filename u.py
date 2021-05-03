#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re
import js2py

js = '''var url = "%s";
var access_key = "%s";
var secret = "%s";

var shaObj = new jsSHA("SHA-1", "TEXT");
	shaObj.setHMACKey(secret, "TEXT");
	shaObj.update(url);
var hmac = shaObj.getHMAC("HEX");

document.getElementById(result_id).innerHTML = "getting results...";

jQuery.ajax({
	url: url
	, headers: {
		'HMAC': hmac
		, 'KEY': access_key
	}
	, type: "POST" // always POST
	, data: {
		"json": json
	}
	, success: function(data, status, jqXHR) {
		document.getElementById(result_id).innerHTML = jqXHR.responseText;
	}
});''' % ('https://wow-sandbox.n-c-s.net/json.pl/objects', '3b4fc64446838561fdef78d18f6e963f', 'b4814b0cfbd19f032d3c61e282cbfa6f')
result = js2py.eval_js(js)
print(result)

