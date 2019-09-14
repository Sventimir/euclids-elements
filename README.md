Euclid's Elements
------------------

This is the Polish translation of parts Euclid's Elements, created as a script
for lectures given on the subject. The translation is based on Greek/English
text available [here](http://farside.ph.utexas.edu/Books/Euclid/Elements.pdf).

To build the document you need:

* LaTeX (I build with Texlive distro, but others should be equally good);
* Python 2.7 or newer (for drawing figures);

It is done with the following command:

    $ pdflatex -shell-escape elements.tex

If it spits a warning about missing refernces, just rebuild and all should be
fine.

During the compilation a lot of intermediate files are created including
some Python scripts and logs of executions of those scripts. They are all
git-ignored and can be safely removed after build. PDF document is all that
matters. Building in formats other than PDF, with compilers other than
`pdflatex` has *not* been tested.
