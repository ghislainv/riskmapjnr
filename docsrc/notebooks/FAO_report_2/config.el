;;; package --- Summary
;;; Configuration for emacs

;;; Commentary:
;;; Use this configuration file through build.sh and Makefile

;;; Code:

;; List of packages to install
(defvar package-list)
(setq package-list '(org
		     org-contrib))

;; Package repositories
(require 'package)
(setq package-archives '(("melpa" . "https://melpa.org/packages/")
			 ("gnu" . "https://elpa.gnu.org/packages/")
			 ("nongnu" . "https://elpa.nongnu.org/nongnu/")))
;; Activate all the packages (in particular autoloads)
(package-initialize)

;; Unless packages are not available locally, dont refresh package archives
;; Refreshing package contents is time-consuming and should be done on demand
(unless package-archive-contents
  (package-refresh-contents))

;; Install the missing packages
(dolist (pkg package-list)
  (unless (package-installed-p pkg)
    (package-install pkg)))

;; Required package
(require 'org)
(require 'ox-latex)

;; Org settings
(setq org-src-preserve-indentation t)
(setq org-export-with-smart-quotes t)
(setq org-startup-with-inline-images t)
(setq org-image-actual-width 600)

;; Add :ignore: tag to ignore headline
(require 'ox-extra)
(ox-extras-activate '(ignore-headlines))

;; Use minted for syntax highlighted
(add-to-list 'org-latex-packages-alist '("" "minted"))
(setq org-latex-listings 'minted)
(setq org-latex-minted-options
      '(("breaklines=true")
	("bgcolor=bg")))

;; Reconfigure org-latex-pdf-process to pass the -shell-escape option
;; (setq org-latex-pdf-process
;;       (mapcar
;;        (lambda (s)
;;          (replace-regexp-in-string "%latex " "%latex -shell-escape " s))
;;        org-latex-pdf-process))
(setq org-latex-pdf-process
      '("pdflatex -shell-escape -interaction nonstopmode -output-directory %o %f"
        "pdflatex -shell-escape -interaction nonstopmode -output-directory %o %f"
        "pdflatex -shell-escape -interaction nonstopmode -output-directory %o %f"))

;; Languages evaluated
(org-babel-do-load-languages
 'org-babel-load-languages
 '((emacs-lisp . t)
  (shell . t)
  (python . t)
  (R . t)
  (screen . t)
  (org . t)
  (makefile . t)))

;; LaTeX class
;; koma article (more modern design than the standard LaTeX classes)
(add-to-list 'org-latex-classes
             '("koma-article" "\\documentclass{scrartcl}"
               ("\\section{%s}" . "\\section*{%s}")
               ("\\subsection{%s}" . "\\subsection*{%s}")
               ("\\subsubsection{%s}" . "\\subsubsection*{%s}")
               ("\\paragraph{%s}" . "\\paragraph*{%s}")
               ("\\subparagraph{%s}" . "\\subparagraph*{%s}")))

;; Bibliography
(require 'oc-csl)
(defvar bibdir (expand-file-name "biblio" default-directory) "Biblio directory.")
(setq org-cite-csl-styles-dir bibdir)

;; Function to export to pdf
(defun export-to-pdf nil
  "Export to pdf.
This function exports an org file to a pdf"
  (find-file "report2.org")
  (org-latex-export-to-pdf nil nil nil nil nil))

;; Call to the function
(export-to-pdf)
(message "----OooooOOooooO----")

;;; config.el ends here
