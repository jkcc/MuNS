/*
 * cAutoSimHash.h
 *
 *  Created on: 19/04/2015
 *      Author: jkct440
 */

#ifndef CAUTOSIMHASH_H_
#define CAUTOSIMHASH_H_


#include <list>
#include <string>
#include <unordered_set>
#include <stdexcept>

//#include "../similarity/dampedSimilarity.h"
#include "cAutoSim.h"
#include "AutoSimInit.h"
#include "../utils/pairUtils.h"



#ifdef _ZERO_SIM_COUNT
	extern
	std::list<int> G_vZeroSimCount;
#endif





class AutoSimHash : public AutoSim
{
protected:

	/** Whether to use hashing. */
	bool m_bHash;

	/** Iceberg filter parameter.  All similarities less than this are estimated. */
	float m_simThres;

	/** Iceberg approximation factor for non-computed similarities. */
	float m_approxFaction;


	/** Use early similarity stop. */
	bool m_bEarlySimStop2;
	float m_earlySimStopThres2;



public:

	AutoSimHash(float dampingFactor, int maxIter, const std::string& sInitAlgor, bool earlySimStop, float earlySimStopThres, bool useInputBalance, float ioBalance, bool useIceberg, float simThres, float approxFaction) throw(std::invalid_argument);
	AutoSimHash(float dampingFactor, int maxIter, float convEpsilon, const std::string& sInitAlgor, bool earlySimStop, float earlySimStopThres, bool useInputBalance, float ioBalance, bool useIceberg, float simThres, float approxFaction) throw(std::invalid_argument);

	virtual ~AutoSimHash();

	virtual float* computeSim(const std::list<int>& vSrc, const std::list<int>& vTar, int edgeNum, int vertNum);


protected:

	/**
	 * Perform the iceberg filtering.
	 */
	void hashFilter(const std::vector< std::vector<int> >& vvInNeigh, const std::vector< std::vector<int> >& vvOutNeigh, C_INT_PAIR_HASH_SET* hValidPair);


	/**
	 * Estimate similarity value.
	 */
	float estimateSim(int vert1, int vert2, const std::vector< std::vector<int> >& vvInNeigh, const std::vector< std::vector<int> >& vvOutNeigh, float beta) const;


	/**
	 * Filter out pairs whose similarity become less than m_earlySimStopThres2.
	 */
	void filterEarlySimPairs(C_INT_PAIR_HASH_SET* phValidPair, const C_INT_PAIR_HASH_MAP* const pmPrevSim, const C_INT_PAIR_HASH_MAP* const pmCurrSim);


	/**
	 * LI distance between two matrices represented as hash tables.
	 */
	float matDiff(const C_INT_PAIR_HASH_SET* const phValidPair, const C_INT_PAIR_HASH_MAP* const pmPrevSim, const C_INT_PAIR_HASH_MAP* const pmCurrSim) const;

}; // end of class AutoSimHash



#endif /* CAUTOSIMHASH_H_ */
