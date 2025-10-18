"""Check FalkorDB version and vector support."""

from llama_index.graph_stores.falkordb import FalkorDBGraphStore

print("Checking FalkorDB infrastructure...")

try:
    gs = FalkorDBGraphStore(
        graph_name="_version_check",
        url="redis://localhost:6379"
    )

    # Check for vector procedures
    result = gs.query("""
        CALL dbms.procedures() YIELD name
        WHERE name CONTAINS 'vector'
        RETURN name
    """)

    print(f"\nVector procedures found: {len(result)}")
    if result:
        for proc in result:
            print(f"  [OK] {proc[0]}")

        # Get signature for queryNodes
        print("\nGetting procedure signature...")
        sig_result = gs.query("""
            CALL dbms.procedures() YIELD name, signature
            WHERE name = 'db.idx.vector.queryNodes'
            RETURN signature
        """)
        if sig_result:
            print(f"  db.idx.vector.queryNodes signature:")
            print(f"    {sig_result[0][0]}")
    else:
        print("  [NONE] NO VECTOR SUPPORT")

    # Try to check version
    try:
        version_result = gs.query("CALL dbms.components() YIELD name, versions RETURN name, versions")
        if version_result:
            print(f"\nFalkorDB components:")
            for comp in version_result:
                print(f"  {comp[0]}: {comp[1]}")
    except:
        print("\nVersion check not supported")

except Exception as e:
    print(f"Error: {e}")
