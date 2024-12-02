import pytest


def test_full_module(tf_module, fixtures_dir) -> None:
    var_file = fixtures_dir / "full-module.tfvars"
    tf = tf_module("spec")

    tf.apply(tf_var_file=var_file)


def test_null_module(tf_module, fixtures_dir) -> None:
    var_file = fixtures_dir / "null-module.tfvars"
    tf = tf_module("spec")

    with pytest.raises(Exception):
        tf.apply(tf_var_file=var_file)
