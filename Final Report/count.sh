#!/bin/bash

TEX=$(texcount -inc -total -brief -sum Chapters/*.tex)
PDFC=$(pdftotext centre.pdf - | wc -w)
DIFF=$( expr $PDFC - $TEX)
echo "Texcount: $TEX"
echo "PDFcentre: $PDFC"
echo "Difference: $DIFF"
