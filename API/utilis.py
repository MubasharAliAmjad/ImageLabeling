def delete_cases(session):
        session_cases = session.case.all()
        for case in session_cases:
            case_categories_types = case.category_type.all()
            for category_type in case_categories_types:
                category_type.options.all().delete()
                if category_type.image.all():
                    # category_type.image.filter().delete()
                    category_type.image.all().delete()
            case.category_type.all().delete()
            case.labels.all().delete()
            if case.reference_folder:       
                 case.reference_folder.image.all().delete()
                 case.reference_folder.delete()
        session.case.all().delete()
        session.slice.all().delete()