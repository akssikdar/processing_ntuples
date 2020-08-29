/** DsetsInfo.cpp functions for getting info from dsets_info_3.xml

implemented with: libxml

compile  with \c -I/usr/include/libxml2
and link with \c -lxml2
*/

#include <stdio.h>
#include <string.h>
#include <iostream>
#include <libxml2/libxml/xpath.h>

#include "UserCode/processing_ntuples/interface/handy_macros.h"


static xmlDocPtr dsets_info_doc; //
static xmlXPathContextPtr xpath_context;
static const xmlChar* xpath_hard_proc = (xmlChar*)"//hard_process";
static xmlXPathObjectPtr hard_procs;
// in fact I do not need this XPath anymore because my XML structure is extremely simple

int DsetsInfo_setup(const char* dsets_info_filename="./dsets_info_3.xml")
	{
	// xml document
	dsets_info_doc = xmlReadFile(dsets_info_filename, NULL, XML_PARSE_HUGE);
	Stopif(!dsets_info_doc, return -1, "Error: unable to parse file %s\n", dsets_info_filename);

	// we'll search for tags with XPath
	// set up the XPath system:
	xpath_context = xmlXPathNewContext(dsets_info_doc);
	Stopif(!xpath_context, return -2, "Error: unable to create the XPath context\n");

	// get the nodes with a given tag name
	hard_procs = xmlXPathEvalExpression(xpath_hard_proc, xpath_context);
	Stopif(!hard_procs, return -3, "Error: could not XPath //hard_process");

	return 0;
	}

int DsetsInfo_free()
	{
	// free all xml resources
	xmlXPathFreeObject(hard_procs);
	xmlXPathFreeContext(xpath_context);
	xmlFreeDoc(dsets_info_doc);
	return 0;
	}

double DsetsInfo_xsec_per_dtag(const char* target_dtag)
	{
	// loop over the hard processes
	for (int i=0; i<hard_procs->nodesetval->nodeNr; i++)
		{
		// the hard process node
		xmlNodePtr hp = hard_procs->nodesetval->nodeTab[i];

		// check if there is a matching dtag
		bool matched_dtag = false;
		xmlNodePtr dset=hp->children;
		for (; dset!=NULL || !matched_dtag; dset=dset->next)
			{
			// confirm this is a dset tag
			if (xmlStrcmp(dset->name, (const xmlChar*)"dset") != 0) continue; // watch out how this comparison works!
			const xmlChar* dtag = xmlGetProp(dset, (const xmlChar*)"dtag");
			matched_dtag = xmlStrcmp(dtag, (const xmlChar*)target_dtag);
			}

		if (matched_dtag)
			{
			return strtod((const char*)xmlGetProp(hp, (const xmlChar*)"xsec"), NULL);
			}
		}

	// default xsec
	return 1.;
	}

const char* DsetsInfo_match_filename_to_dtag(const char* filename)
	{
	// loop over the hard processes
	for (int i=0; i<hard_procs->nodesetval->nodeNr; i++)
		{
		// the hard process node
		xmlNodePtr hp = hard_procs->nodesetval->nodeTab[i];

		// check if there is a matching dtag
		xmlNodePtr dset=hp->children;
		for (; dset!=NULL; dset=dset->next)
			{
			// confirm this is a dset tag
			if (xmlStrcmp(dset->name, (const xmlChar*)"dset") != 0) continue; // watch out how this comparison works!
			// check if filename contains dtag
			const xmlChar* dtag = xmlGetProp(dset, (const xmlChar*)"dtag");
			char* match = strstr((char*)filename, (const char*)dtag);
			if (match)
				{
				return (const char*) dtag;
				}
			}
		}

	// not found dtag
	return NULL;
	}

int main (int argc, char *argv[])
{
// skip the program name
argc--;
const char* exec_name = argv[0];
argv++;

if (argc < 1)
	{
	std::cout << "Usage:" << " path/to/dsets_info.xml" << std::endl;
	exit(0);
	}

// the dsets_info filename
const char* dsets_info_filename = argv[0];

// xml document
dsets_info_doc = xmlReadFile(dsets_info_filename, NULL, XML_PARSE_HUGE);
Stopif(!dsets_info_doc, return -1, "Error: unable to parse file %s\n", dsets_info_filename);

// we'll search for tags with XPath
// set up the XPath system:
xmlXPathContextPtr xpath_context = xmlXPathNewContext(dsets_info_doc);
Stopif(!xpath_context, return -2, "Error: unable to create the XPath context\n");

// get the nodes with a given tag name
xpath_hard_proc = (xmlChar*)"//hard_process";
xmlXPathObjectPtr hard_procs = xmlXPathEvalExpression(xpath_hard_proc, xpath_context);
Stopif(!hard_procs, return -3, "Error: could not XPath //hard_process");

// loop over found tags
for (int i=0; i<hard_procs->nodesetval->nodeNr; i++)
	{
	// dumping all content
	//printf("%s\n", xmlNodeGetContent(hard_procs->nodesetval->nodeTab[i]));
	// print their names
	//printf("%s\n", hard_procs->nodesetval->nodeTab[i]->name);
	xmlNodePtr hp = hard_procs->nodesetval->nodeTab[i];

	// get xsec and dtags
	if (xmlHasProp(hp, (const xmlChar*)"xsec"))
		printf("xsec = %10.3g\t", atof((const char*)xmlGetProp(hp, (const xmlChar*)"xsec")));
	else
		printf("xsec = %10s", "NAN");

	// the dsets are easy: the children are dsets + some random "text" files?? -- some internal XML crap
	xmlNodePtr dset=hp->children;
	for (; dset!=NULL; dset=dset->next)
		{
		if (xmlStrcmp(dset->name, (const xmlChar*)"dset") != 0) continue; // watch out how this comparison works!
		printf(" %20s", (const char*)xmlGetProp(dset, (const xmlChar*)"dtag"));
		}
	printf("\n");
	}

// free all xml resources
xmlXPathFreeObject(hard_procs);
xmlXPathFreeContext(xpath_context);
xmlFreeDoc(dsets_info_doc);
return 0;
}
