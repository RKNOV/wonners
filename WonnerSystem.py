async def get_user_data(user_id, field):
    user = await db.users.find_one({'user_id': user_id})
    return user.get(field, 0) if user else 0

async def update_user_data(user_id, field, value):
    await db.users.update_one({'user_id': user_id}, {'$set': {field: value}}, upsert=True)

async def add_referral(user_id, referrer_id):
    count = await db.user_referrals.count_documents({'user_id': user_id})
    if count < 2:
        try:
            await db.user_referrals.insert_one({'user_id': user_id, 'referrer_id': referrer_id})
        except Exception:
            pass

async def get_referrals(user_id):
    cursor = db.user_referrals.find({'user_id': user_id}).sort('_id', 1)
    return await cursor.to_list(length=None)

async def increase_user_steps(user_id, steps):
    s = await get_user_data(user_id, 'steps')
    ns = s + steps
    w = (ns // 100 - s // 100) * 15
    if w > 0:
        referrals = await get_referrals(user_id)
        if len(referrals) >= 1:
            b1 = int(w * 0.0013 + 0.5)
            if b1 > 0:
                ref1 = referrals[0]['referrer_id']
                woncoins = await get_user_data(ref1, 'woncoins')
                await update_user_data(ref1, 'woncoins', woncoins + b1)
        if len(referrals) >= 2:
            b2 = int(w * 0.0020 + 0.5)
            if b2 > 0:
                ref2 = referrals[1]['referrer_id']
                woncoins = await get_user_data(ref2, 'woncoins')
                await update_user_data(ref2, 'woncoins', woncoins + b2)
    await db.users.update_one({'user_id': user_id}, {'$set': {'steps': ns}, '$inc': {'woncoins': w}}, upsert=True)
