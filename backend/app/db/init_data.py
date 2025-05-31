"""
Initialize default data for the application
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.document import DocumentCategory
from ..schemas.document import DocumentCategoryCreate


async def initialize_categories(db: AsyncSession) -> None:
    """
    Initialize default document categories if they don't exist
    """
    # Check if categories already exist
    stmt = select(DocumentCategory)
    result = await db.execute(stmt)
    existing_categories = result.scalars().all()
    
    if existing_categories:
        print(f"Categories already exist: {len(existing_categories)} found")
        return
    
    # Default categories pentru documente legale românești
    default_categories = [
        {
            "name": "Urbanism și Construcții",
            "description": "Autorizații de construire, certificates de urbanism, planuri urbanistice, regulamente de construire",
            "icon": "building",
            "color": "#3B82F6"
        },
        {
            "name": "Fiscal și Taxe Locale",
            "description": "Hotărâri fiscale, regulamente de impozitare, declarații fiscale, taxe și impozite locale",
            "icon": "file",
            "color": "#10B981"
        },
        {
            "name": "Servicii Sociale și Asistență",
            "description": "Regulamente de asistență socială, ajutoare sociale, servicii pentru persoane vulnerabile",
            "icon": "users",
            "color": "#F59E0B"
        },
        {
            "name": "Transport și Infrastructură",
            "description": "Regulamente de circulație, autorizări transport, amenajări rutiere, transport public",
            "icon": "check",
            "color": "#EF4444"
        },
        {
            "name": "Mediu și Protecția Naturii",
            "description": "Autorizări de mediu, regulamente ecologice, protecția naturii, salubritate publică",
            "icon": "file",
            "color": "#10B981"
        },
        {
            "name": "Administrativ și Organizare",
            "description": "Hotărâri administrative, organigramă, regulamente de organizare și funcționare",
            "icon": "file",
            "color": "#6B7280"
        },
        {
            "name": "Educație și Cultură",
            "description": "Regulamente școlare, proiecte educaționale, evenimente culturale, biblioteci publice",
            "icon": "file",
            "color": "#8B5CF6"
        },
        {
            "name": "Sănătate Publică",
            "description": "Regulamente sanitare, autorizări sanitare, campanii de sănătate publică",
            "icon": "users",
            "color": "#EC4899"
        },
        {
            "name": "Ordine Publică și Siguranță",
            "description": "Regulamente de ordine publică, măsuri de siguranță, prevenirea criminalității",
            "icon": "check",
            "color": "#DC2626"
        },
        {
            "name": "Dezvoltare Economică",
            "description": "Proiecte de dezvoltare, investiții publice, programe economice, achiziții publice",
            "icon": "building",
            "color": "#0369A1"
        },
        {
            "name": "Participare Cetățenească",
            "description": "Consultări publice, petiții, dezbatere publică, transparență decizională",
            "icon": "users",
            "color": "#7C3AED"
        },
        {
            "name": "Resurse Umane și Personal",
            "description": "Regulamente de personal, concursuri, organizarea aparatului public local",
            "icon": "file",
            "color": "#059669"
        }
    ]
    
    # Create categories
    created_count = 0
    for cat_data in default_categories:
        try:
            db_category = DocumentCategory(
                name=cat_data["name"],
                description=cat_data["description"],
                icon=cat_data["icon"],
                color=cat_data["color"]
            )
            db.add(db_category)
            created_count += 1
        except Exception as e:
            print(f"Error creating category {cat_data['name']}: {e}")
    
    try:
        await db.commit()
        print(f"✅ Created {created_count} default categories successfully")
    except Exception as e:
        await db.rollback()
        print(f"❌ Error committing categories: {e}")


async def initialize_default_data(db: AsyncSession) -> None:
    """
    Initialize all default data
    """
    print("🔄 Initializing default data...")
    await initialize_categories(db)
    print("✅ Default data initialization complete") 