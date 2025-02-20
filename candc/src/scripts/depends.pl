# C&C NLP tools
# Copyright (c) Universities of Edinburgh, Oxford and Sydney
# Copyright (c) James R. Curran
#
# This software is covered by a non-commercial use licence.
# See LICENCE.txt for the full text of the licence.
#
# If LICENCE.txt is not included in this distribution
# please email candc@it.usyd.edu.au to obtain a copy.

$DEPENDS = shift;

while(@ARGV){
  $SOURCE = shift;
  $SOURCE =~ s|^./||;
  $OBJECT = $SOURCE;
  $OBJECT =~ s/\.cc$/\.o/;
  $PATH = $SOURCE;
  $PATH =~ s|[^/]+$||;

  warn "$DEPENDS $SOURCE | sed \"s|^[^ ]|$PATH&|\"\n";
  system "$DEPENDS $SOURCE | sed \"s|^[^ ]|$PATH&|\"";
  print "\n";
}
