from base import ChromaManager
import asyncio

NAGA_HILLS_COLLECTION_NAME = "1905_Naga_Hills_and_Manipur_by_Allen"
SCIFACT_COLLECTION_NAME = "scifact_collection"
SCIDOCS_COLLECTION_NAME = "scidocs_collection"

query = "To improve energy efficiency in copper electrowinning, different technologies have been developed. These include electrode positioning capping boards and 3-D grids, electrode spacers, and segmented intercell bars. This paper introduces a design concept to avoid electrode open circuits and reduce contact resistances. The design is based on a female tooth shape for the contacts on the intercell bar. This leads to improved electrode alignment, reduced contact resistances, easier contact cleaning, and ensured electrical contact for the electrodes. It results in lower operational temperature for the electrodes, reduced plant housekeeping, increased lifespan for capping boards, and higher rate of grade A copper production. The comparative results presented should be a useful guideline for any type of intercell bar. Improvements in production levels and energy efficiency should reach 0.5% and 3%, respectively. A 3-D finite-element-based analysis and industrial measurements are used to verify the results."

async def main():
    manager = ChromaManager(collection_name=SCIDOCS_COLLECTION_NAME)

    await manager.connect()

    result = await manager.query([query], n_results=10)
    print(result)

    await manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())