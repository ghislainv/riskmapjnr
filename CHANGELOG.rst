Changelog
=========

riskmapjnr 1.2
--------------

* Improving documentation.
* Bug corrections:

  - Make sure that `fcc_file` is projected to compute distances.
  - Let the user set Agg backend for matplotlib when DISPLAY is not found.
  - Close and join the pool execution in `makemap()`.

* This version is running without issues in `SEPAL <https://sepal.io>`_.

riskmapjnr 1.1
--------------

* Removing unnecessary output files.

riskmapjnr 1.0
--------------

* First stable release.
* Parallel computation for `makemap()`.
* Benchmark to estimate advantage of parallel computing.
* New tutorials on large jurisdictions (countries).
* Bug corrections:
  
  - Correction of the annual deforestation rate formula.
  - Correction of the validation step using maps at the start of the validation period.
  - Correction of the final risk map at the end of the validation period.
  
riskmapjnr 0.1
--------------

* First alpha release of the package. Must be thoroughly tested.
  
