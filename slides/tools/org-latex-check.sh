#!/usr/bin/env bash
# Render every \(math\) fragment of an Org file with Org's own previewer, as
# `#+startup: latexpreview` would, and report the ones that fail.
#   slides/tools/org-latex-check.sh units/01-polyhedra-farkas/GLOSSARY.org
set -euo pipefail
f=$(realpath "$1")
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
emacs --batch --eval "
(progn
  (require 'org) (require 'org-element)
  (setq temporary-file-directory \"$tmp/\")
  (find-file \"$f\")
  (let ((ok 0) (bad 0) (i 0)
        (opts (plist-put (plist-put (copy-sequence org-format-latex-options) :foreground \"Black\") :background \"White\")))
    (org-element-map (org-element-parse-buffer) 'latex-fragment
      (lambda (fr)
        (let ((v (org-element-property :value fr)) (out (format \"$tmp/f%03d.png\" (setq i (1+ i)))))
          (condition-case nil
              (progn (org-create-formula-image v out opts 'forbuffer 'dvipng)
                     (if (file-exists-p out) (setq ok (1+ ok)) (setq bad (1+ bad)) (princ (format \"NO IMAGE: %s\n\" v))))
            (error (setq bad (1+ bad)) (princ (format \"FAIL: %s\n\" v)))))))
    (let ((untagged 0))
      (org-element-map (org-element-parse-buffer) 'item
        (lambda (it) (unless (org-element-property :tag it) (setq untagged (1+ untagged)))))
      (princ (format \"%d rendered, %d failed, %d list items without a term\n\" ok bad untagged)))))" 2>&1 | grep -v '^Loading'
